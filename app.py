# LICENSE: https://github.com/openslide/openslide/blob/master/lgpl-2.1.txt
from flask import Flask, send_file, render_template, redirect, request, abort, session, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from openslide.deepzoom import DeepZoomGenerator
from QueueDictClass import OurDataStructure
from flask_sqlalchemy import SQLAlchemy
import xml.etree.ElementTree as ET
import customLogger
import HelperClass
import openslide
import imageList
import traceback
import binascii
import json
import os


nestedImageList = {}
imagePathLookupTable = {}

deepZoomList = OurDataStructure()

dateTime = customLogger.DateTime()
logger = customLogger.StartLogging()

app = Flask(__name__)
HelperClass.ConfigureApp(app)


db = SQLAlchemy(app)
db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
@login_required
def Main():
    ImageListHTML = GenerateImageListHtml()
    GetAvailableImages()
    return render_template("index.html", imageList=ImageListHTML)


@app.route('/images/<filename>')
def LoadControlImages(filename):
    return send_file("static/images/" + filename)


@app.route('/app/<folder>/<filename>')
@login_required
def changeImage(folder, filename):
    global imagePathLookupTable
    session["ID"] = binascii.hexlify(os.urandom(20))
    path = "//home/prosjekt"+imagePathLookupTable[folder+"/"+filename]
    image = openslide.OpenSlide(path)
    logger.log(25, HelperClass.LogFormat() + current_user.username + " requested image " + filename)
    deepZoomGen = DeepZoomGenerator(image, tile_size=254, overlap=1, limit_bounds=False)
    deepZoomList.append(session["ID"], deepZoomGen)
    return deepZoomGen.get_dzi("jpeg")
  
  
@app.route('/app/<dummy>/<dummy2>/<level>/<tile>')
@login_required
def GetTile(dummy, dummy2, level, tile):
    col, row = GetNumericTileCoordinatesFromString(tile)
    deepZoomGen = deepZoomList.get(session["ID"])
    img = deepZoomGen.get_tile(int(level), (int(col), int(row)))
    return HelperClass.serve_pil_image(img)


@app.route('/postxml/<foldername>/<filename>', methods=["POST"])
@login_required
def PostXML(foldername, filename):
    try:
        folder = "//home/prosjekt/Histology/thomaso/"
        file = foldername+"[slash]"+filename + ".xml"
        if not os.path.isfile(folder+file):
            Annotations = ET.Element("Annotations")
            Annotation = ET.SubElement(Annotations, "Annotation")
            ET.SubElement(Annotation, "Regions")
            tree = ET.ElementTree(Annotations)
            tree.write(folder+file)

        InsertImageToDB(file.replace(".xml", ""))

        tree = ET.parse(folder+file)
        regions = tree.getroot()[0][0]

        xml = request.data.decode("utf-8")
        xmlThing = ET.fromstring(xml)
        xmlTree = ET.ElementTree(xmlThing)

        newRegions = xmlTree.getroot()[0][0]
        moreRegions = newRegions.findall("Region")

        for region in moreRegions:
            regions.append(region)
            formatedTags = region.attrib["tags"]
            tags = formatedTags.split("|")
            grade = region.attrib["grade"]
            InsertDrawingsToDB(file.replace(".xml", ""), tags, grade)

        tree.write(folder+file)
    except:
        traceback.print_exc()
        return "", 500
    return "", 200


def InsertImageToDB(imagePath):
    query = "select ImagePath from images where ImagePath = '{}';".format(imagePath)
    queryResult = db.engine.execute(query)
    result = [row[0] for row in queryResult]

    if not result:
        db.engine.execute("insert into images(ImagePath) values('{}');".format(imagePath))

def InsertDrawingsToDB(imagePath, tags, grade):
    for tag in tags:
            queryResult = db.engine.execute("select ImagePath from annotations where tag = '{}'"
                                            " and ImagePath = '{}'".format(tag, imagePath))
            result = [row[0] for row in queryResult]

            if not result:
                db.engine.execute("insert into annotations(ImagePath, Tag, Grade) values('{}', '{}', {});"
                              .format(imagePath, tag, grade))
            else:
                dbResult = db.engine.execute("select ImagePath, Tag, Grade from annotations where ImagePath = '{}'"
                                      "and Tag = '{}' and Grade = {};".format(imagePath, tag, grade))

                resultDb = [res[0] for res in dbResult]
                
                if not resultDb:
                    db.engine.execute("insert into annotations(ImagePath, Tag, Grade) values('{}', '{}', {});"
                                      .format(imagePath, tag, grade))

@app.route('/getxml/<foldername>/<filename>')
@login_required
def GetXML(foldername, filename):
    folder = "//home/prosjekt/Histology/thomaso/"
    file = foldername+"[slash]"+filename
    foo = file.replace("%20", " ")
    if os.path.isfile(folder+foo):
        return send_from_directory(folder, foo)
    return "", 500


def GetAvailableImages():
    global nestedImageList
    global imagePathLookupTable
    imagePathLookupTable, err = imageList.ReadImageListFromFile()
    if err is not "":
        abort(500)
    else:
        nestedImageList = imageList.BuildNested(imagePathLookupTable)


@app.route('/favicon.ico')
def favicon():
    return send_file("static/images/favicon.ico", mimetype="image/jpeg")


@app.route("/addTag", methods=["POST"])
def addTags():
    tag = json.loads(request.data)["tag"]
    newTag = Tags(tag)
    db.session.add(newTag)
    db.session.commit()
    return "", 200


@app.route("/updateTags", methods=["GET", "POST"])
def updateTags():
    tuppletags = Tags.query.with_entities(Tags.Name)
    tags = {"tags": []}
    for tag in tuppletags:
        tags["tags"].append(tag[0])

    return json.dumps(tags), 200


@app.route("/searchTags", methods=["POST"])
def searchTags():
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
def getCurrentUser():
    return str(current_user.username), 200

@app.route('/authenticated')
def isAuthenticated():
    if not current_user.is_authenticated:
        return "", 401
    return "", 200


def GetNumericTileCoordinatesFromString(tile):
    col, row = str.split(tile, "_")
    row = str.replace(row, ".jpeg", "")
    return col, row


@app.errorhandler(500)
def handle500(error):
    return "SOMETHING BAD HAPPENED ON OUR END", 500

def GenerateImageListHtml():
    global nestedImageList
    return imageList.GetImageListHTML(nestedImageList)


@app.route("/login", methods=["GET", "POST"])
def Login():
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user is not None and username == user.username and user.check_password(password):
            logger.log(25, HelperClass.LogFormat() + username + " logged in")
            login_user(user)
            return redirect("/")
        else:
            logger.log(25, HelperClass.LogFormat() + "Attempted log in with username: " + username)
            return render_template("login.html", className = "warning", message="Wrong username or password")
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
@login_required
def Register():
    if str(current_user.type) != "Admin":
        abort(401)
    if request.method == "POST" and request.form["username"].lower() is not None:
        registerUsername = request.form["username"].lower()
        firstPassField = request.form["firstPassField"]
        userType = request.form.get("userType")

        if User.query.filter_by(username=registerUsername).first() is not None:
            return render_template("register.html", className = "warning", message = "Username already exists.")

        if request.form["secondPassField"] != firstPassField:
            return render_template("register.html", className = "warning", message = "Passwords does not match")

        newUser = User(registerUsername, firstPassField, userType)
        db.session.add(newUser)
        db.session.commit()
        logger.log(25, HelperClass.LogFormat() + current_user.username + " registered a new user: " + registerUsername)
        return redirect("/")

    return render_template("register.html")


@login_manager.user_loader
def user_login(Username):
    return User.query.get(Username)


@app.route("/logout")
@login_required
def Logout():
    logger.log(25, HelperClass.LogFormat() + current_user.username + " logged out")
    logout_user()
    return render_template("login.html", className="info", message="Logged out")


@login_manager.unauthorized_handler
def CatchNotLoggedIn():
    return redirect("/login")


@app.errorhandler(401)
def not_found(error):
    return render_template('401.html'), 401


class User(UserMixin, db.Model):
    id = db.Column("ID", db.Integer, primary_key=True)
    username = db.Column("Username", db.String, )
    password = db.Column("Password", db.String)
    type = db.Column("Type", db.String)

    def __init__(self, username, password, type):
        self.username = username
        self.password = self.set_password(password)
        self.type = type

    def set_password(self, password):
        return generate_password_hash(password)

    def get_password(self):
        return self.password

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Tags(db.Model):
    Name = db.Column("Name", db.String, primary_key=True)

    def __init__(self, Name):
        self.Name = Name


class Images(db.Model):
    ImageID = db.Column("ImageID", db.Integer, primary_key=True)
    ImagePath = db.Column("ImagePath", db.String)

    def __init__(self, ImageID, ImagePath):
        self.ImageID = ImageID
        self.ImagePath = ImagePath


class Annotations(db.Model):
    ID = db.Column("ID", db.Integer, primary_key=True)
    ImagePath = db.Column("ImagePath", db.String, db.ForeignKey("Images.ImagePath"))
    Tag = db.Column("Tag", db.String)
    Grade = db.Column("Grade", db.Integer)

    def __init__(self, ImagePath, Tag, Grade):
        self.ImagePath = ImagePath
        self.Tag = Tag
        self.Grade = Grade


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8082, threaded=True)

