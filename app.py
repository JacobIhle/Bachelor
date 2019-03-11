# LICENSE: https://github.com/openslide/openslide/blob/master/lgpl-2.1.txt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import Flask, send_file, render_template, redirect, request, abort
from werkzeug.security import generate_password_hash, check_password_hash
from openslide.deepzoom import DeepZoomGenerator
from flask_sqlalchemy import SQLAlchemy
import customLogger
import openslide
import HelperClass
import imageList
from collections import deque

nestedImageList = {}
imagePathLookupTable = {}

image = None
deepZoomGen = None

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


@app.route('/app/<filename>')
def changeImage(filename):
    global image; global deepZoomGen; global imagePathLookupTable
    path = "//home/prosjekt"+imagePathLookupTable[filename]
    print(path)
    image = openslide.OpenSlide(path)
    logger.log(25, HelperClass.LogFormat() + current_user.username + " requested image " + filename)
    deepZoomGen = DeepZoomGenerator(image, tile_size=254, overlap=1, limit_bounds=False)
    return deepZoomGen.get_dzi("jpeg")
  
  
@app.route('/app/<dummy>/<level>/<tile>')
def GetTile(dummy, level, tile):
    col, row = GetNumericTileCoordinatesFromString(tile)
    img = deepZoomGen.get_tile(int(level), (int(col), int(row)))
    return HelperClass.serve_pil_image(img)

  
#TODO
#FOR RUNNING ON UNIX SERVER
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


def GetNumericTileCoordinatesFromString(tile):
    col, row = str.split(tile, "_")
    row = str.replace(row, ".jpeg", "")
    return col, row


@app.errorhandler(500)
def handle500(error):
    return "SOMETHING BAD HAPPENED ON OUR END, SAWWIII", 500

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
#@login_required
def Register():
    ## DONT PUSH THIS TO GORINA BEFORE THE DATABASE IS UPDATED TO SUPPORT DIFFERENT TYPE OF USERS
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
        #logger.log(25, HelperClass.LogFormat() + current_user.username + " registered a new user: " + registerUsername)
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


# Redirects users to login screen if they are not logged in.
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

class OurDataStructure():
    dictionary = {}
    doubleSidedQueue = deque()
    counter = 0

    def append(self, key, deepZoomGen):

        try:
            if self.counter >= 1000:
                oldestKey = self.doubleSidedQueue.pop()
                self.doubleSidedQueue.appendleft(key)

                self.dictionary[key] = deepZoomGen
                self.dictionary.pop(oldestKey, None)
            else:
                self.doubleSidedQueue.appendleft(key)
                self.dictionary[key] = deepZoomGen
                self.counter += 1
            return True
        except:
            return False

    def get(self, key):
        try:
            return self.dictionary[key]
        except:
            return None


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8082, threaded=True)

