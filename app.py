#LICENSE: https://github.com/openslide/openslide/blob/master/lgpl-2.1.txt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import Flask, send_file, render_template, send_from_directory, redirect, request, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from openslide.deepzoom import DeepZoomGenerator
from flask_sqlalchemy import SQLAlchemy
import customLogger
import openslide
import HelperClass


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
    return render_template("index.html")


@app.route('/images/<filename>')
def LoadControlImages(filename):
    return send_file("static/images/"+filename)


@app.route('/scnImages/<filename>')
def changeImage(filename):
    global image; global deepZoomGen
    logger.log(25, HelperClass.LogFormat() + current_user.username + " requested image " + filename)
    image = openslide.OpenSlide("scnImages/"+filename+".scn")
    deepZoomGen = DeepZoomGenerator(image, tile_size=254, overlap=1, limit_bounds=False)
    return deepZoomGen.get_dzi("jpeg")


@app.route('/scnImages/<dummyVariable>/<level>/<tile>')
def GetTile(dummyVariable, level, tile):
    col, row = HelperClass.GetNumericTileCoordinatesFromString(tile)
    img = deepZoomGen.get_tile(int(level), (int(col), int(row)))
    return HelperClass.serve_pil_image(img)


@app.route('/<root>/<imageID>/<file>')
def GetDzi(root, imageID, file):
    return send_file(root+"/"+imageID+"/"+file)


@app.route('/favicon.ico')
def favicon():
    return send_file("static/images/favicon.ico", mimetype="image/jpeg")


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
        registerPassword = request.form["password"]

        newUser = User(registerUsername, registerPassword)
        db.session.add(newUser)
        db.session.commit()
        logger.log(25, HelperClass.LogFormat() + current_user.username + " registered a new user: " + registerUsername)
        redirect("/login")

    return render_template("register.html")


@login_manager.user_loader
def user_login(Username):
    return User.query.get(Username)


#TODO: Remove before production, this breaks pretty much all security we have implemented
@app.route("/hack")
def ForceLogin():
    login_user(User.query.filter_by(username="Ridalor").first())
    return redirect("/")


@app.route("/logout")
@login_required
def Logout():
    logger.log(25, HelperClass.LogFormat() + current_user.username + " logged out")
    logout_user()
    return render_template("login.html", type="logout", message = "You are now logged out")


# Redirects users to login screen if they are not logged in.
@login_manager.unauthorized_handler
def CatchNotLoggedIn():
    return redirect("/login")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, threaded=True, ssl_context=("local.com.cert", "local.com.key"))


class User(UserMixin, db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column("Username", db.String,)
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

