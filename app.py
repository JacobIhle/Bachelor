# LICENSE: https://github.com/openslide/openslide/blob/master/lgpl-2.1.txt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import Flask, send_file, render_template, send_from_directory, redirect, request, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from openslide.deepzoom import DeepZoomGenerator
from flask_sqlalchemy import SQLAlchemy
import customLogger
import openslide
import HelperClass
import imageList

nestedImageList = {}
imagePathLookupTable = {}

dateTime = customLogger.DateTime()
logger = customLogger.StartLogging()

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
    GetAvailableImages()
    return render_template("index.html")


@app.route('/images/<filename>')
def LoadControlImages(filename):
    return send_file("static/images/" + filename)


# TODO
# FOR RUNNING ON UNIX SERVER

@app.route('/app/<filename>')
def changeImage(filename):
    global image; global deepZoomGen; global imagePathLookupTable
    path = imagePathLookupTable[filename]
    print(path)
    image = openslide.OpenSlide(path)
    logger.log(25, HelperClass.LogFormat() + current_user.username + " requested image " + filename)
    deepZoomGen = DeepZoomGenerator(image, tile_size=254, overlap=1, limit_bounds=False)
    return deepZoomGen.get_dzi("jpeg")
  
  
@app.route('/app/<level>/<tile>')
def GetTile(level, tile):
    col, row = GetNumericTileCoordinatesFromString(tile)
    img = deepZoomGen.get_tile(int(level), (int(col), int(row)))
    return HelperClass.serve_pil_image(img)

  
#TODO
#FOR RUNNING ON UNIX SERVER
def GetAvailableImages():
    global nestedImageList
    global imagePathLookupTable
    imagePathLookupTable = imageList.ReadImageListFromFile()
    nestedImageList = imageList.BuildNested(imagePathLookupTable)


@app.route('/favicon.ico')
def favicon():
    return send_file("static/images/favicon.ico", mimetype="image/jpeg")


def GetNumericTileCoordinatesFromString(tile):
    col, row = str.split(tile, "_")
    row = str.replace(row, ".jpeg", "")
    return col, row


def GenerateImageListHtml():
    global nestedImageList
    return imageList.CallFromJinja(nestedImageList)


app.jinja_env.globals.update(GenerateImageList=GenerateImageListHtml)


# User handling methods
@app.route("/login", methods=["GET", "POST"])
def Login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user is not None and username == user.username and user.check_password(password):
            logger.log(25, HelperClass.LogFormat() + username + " logged in")
            login_user(user)
            return redirect("/")
        else:
            logger.log(25, HelperClass.LogFormat() + "Attempted loggin with username: " + username)
            return render_template("login.html", type="login", message="Wrong username or password")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
@login_required
def Register():
    if request.method == "POST":
        registerUsername = request.form["username"]
        registerPassword = request.form["firstPassField"]

        newUser = User(registerUsername, registerPassword)
        db.session.add(newUser)
        db.session.commit()
        logger.log(25, HelperClass.LogFormat() + current_user.username + " registered a new user: " + registerUsername)
        redirect("/login")

    return render_template("register.html")


@login_manager.user_loader
def user_login(Username):
    return User.query.get(Username)


@app.route("/logout")
@login_required
def Logout():
    logger.log(25, HelperClass.LogFormat() + current_user.username + " logged out")
    logout_user()
    return render_template("login.html", type="logout", message="You are now logged out")


# Redirects users to login screen if they are not logged in.
@login_manager.unauthorized_handler
def CatchNotLoggedIn():
    return redirect("/login")


class User(UserMixin, db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column("Username", db.String, )
    password = db.Column("Password", db.String)

    def __init__(self, username, password):
        self.username = username
        self.password = self.set_password(password)

    def set_password(self, password):
        return generate_password_hash(password)

    def get_password(self):
        return self.password

    def check_password(self, password):
        return check_password_hash(self.password, password)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8082, threaded=True)
