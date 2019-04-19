# LICENSE: https://github.com/openslide/openslide/blob/master/lgpl-2.1.txt
from flask import Flask, send_file, render_template, redirect, request, abort, session, send_from_directory
from flask_login import LoginManager, logout_user, login_required, current_user
from openslide.deepzoom import DeepZoomGenerator
from QueueDictClass import SessionDeepzoomStorage
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
import customLogger
import configuration
import openslide
import imageList
import binascii
import json
import os
import asyncio

nestedImageList = {}
imagePathLookupTable = {}

deepZoomList = SessionDeepzoomStorage()

logger = customLogger.StartLogging()

app = Flask(__name__)
configuration.ConfigureApp(app)


db = SQLAlchemy(app)
db.create_all()


import xmlAndDB
import dbClasses
import userHandling


login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
@login_required
async def Main():
    # GetAvailableImages()
    await GetAvailableImages()
    ImageListHTML = GenerateImageListHtml()
    return render_template("index.html", imageList=ImageListHTML)


@app.route('/images/<filename>')
def LoadControlImages(filename):
    return send_file("static/images/" + filename)


@app.route('/app/<folder>/<filename>')
@login_required
def ChangeImage(folder, filename):
    global imagePathLookupTable
    session["ID"] = binascii.hexlify(os.urandom(20))
    path = "//home/prosjekt"+imagePathLookupTable[folder+"/"+filename]
    image = openslide.OpenSlide(path)
    logger.log(25, configuration.LogFormat() + current_user.username + " requested image " + filename)
    deepZoomGen = DeepZoomGenerator(image, tile_size=254, overlap=1, limit_bounds=False)
    deepZoomList.append(session["ID"], deepZoomGen)
    return deepZoomGen.get_dzi("jpeg")
  
  
@app.route('/app/<dummy>/<dummy2>/<level>/<tile>')
@login_required
def GetTile(dummy, dummy2, level, tile):
    col, row = GetNumericTileCoordinatesFromString(tile)
    deepZoomGen = deepZoomList.get(session["ID"])
    img = deepZoomGen.get_tile(int(level), (int(col), int(row)))
    return ServePilImage(img)


@app.route('/postxml/<foldername>/<filename>', methods=["POST"])
@login_required
def PostXML(foldername, filename):
    return xmlAndDB.saveFromXml(foldername, filename)


@app.route('/getxml/<foldername>/<filename>')
@login_required
def GetXML(foldername, filename):
    return xmlAndDB.LoadFromXml(foldername, filename)


@app.route("/addTag", methods=["POST"])
@login_required
def AddTags():
    tag = json.loads(request.data)["tag"]
    newTag = dbClasses.Tags(tag)
    db.session.add(newTag)
    db.session.commit()
    return "", 200


@app.route("/updateTags", methods=["GET", "POST"])
@login_required
def UpdateTags():
    tuppletags = dbClasses.Tags.query.with_entities(dbClasses.Tags.Name)
    tags = {"tags": []}
    for tag in tuppletags:
        tags["tags"].append(tag[0])

    return json.dumps(tags), 200


@app.route("/searchTags", methods=["POST"])
@login_required
def SearchTags():
    tag = json.loads(request.data)["tag"]
    queryString = "select i.ImagePath from images as i inner join annotations a on (i.ImagePath = a.ImagePath) where a.tag = '{}';".format(tag)
    query = db.engine.execute(queryString)
    images = []

    for image in query:
        images.append(image[0])

    jsonImages = {"images": images}

    return json.dumps(jsonImages), 200


@app.route("/getCurrentUser")
@login_required
def GetCurrentUser():
    return str(current_user.username), 200


@app.route('/authenticated')
def IsAuthenticated():
    if not current_user.is_authenticated:
        return "", 401
    return "", 200


@app.route("/logout")
@login_required
def Logout():
    logger.log(25, configuration.LogFormat() + current_user.username + " logged out")
    logout_user()
    return render_template("login.html", className="info", message="Logged out")


@app.route("/login", methods=["GET", "POST"])
def Login():
    return userHandling.handleLogin()


@app.route("/register", methods=["GET", "POST"])
@login_required
def Register():
    return userHandling.handleRegister()


@app.route('/favicon.ico')
def Favicon():
    return send_file("static/images/favicon.ico", mimetype="image/jpeg")


# Automatically called by login_manager to update session token.
@login_manager.user_loader
def RefreshLoginToken(Username):
    return dbClasses.User.query.get(Username)


@login_manager.unauthorized_handler
def CatchNotLoggedIn():
    return redirect("/login")


@app.errorhandler(401)
def Handle401(error):
    return render_template('401.html'), 401


@app.errorhandler(500)
def Handle500(error):
    return "If you see this, something went wrong on our end", 500


def GetAvailableImages():
    global nestedImageList
    global imagePathLookupTable
    imagePathLookupTable, err = imageList.ReadImageListFromFile()
    if err is not "":
        abort(500)
    else:
        nestedImageList = imageList.BuildNested(imagePathLookupTable)


def ServePilImage(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=80)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


def GetNumericTileCoordinatesFromString(tile):
    col, row = str.split(tile, "_")
    row = str.replace(row, ".jpeg", "")
    return col, row


def GenerateImageListHtml():
    global nestedImageList
    return imageList.GetImageListHTML(nestedImageList)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8082, threaded=True)

