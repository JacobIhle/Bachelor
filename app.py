#LICENSE: https://github.com/openslide/openslide/blob/master/lgpl-2.1.txt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import Flask, send_file, render_template, send_from_directory, redirect, request, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from openslide.deepzoom import DeepZoomGenerator
from flask_sqlalchemy import SQLAlchemy
from time import gmtime, strftime
from io import BytesIO
import customLogger
import openslide
import logging
import os

allAvailableImages = {}
dateTime = customLogger.DateTime()
logger = customLogger.StartLogging()

# Creates a new logging file for this session
filename = str("logging\\" + str(strftime("%Y_%m_%d %H.%M.%S", gmtime())).replace(" ", "_") + ".txt")
logging.basicConfig(filename=filename, level=logging.WARNING)

image = None
deepZoomGen = None

with open("Login.txt", 'r') as f:
    dbUser, dbPassword = f.readline().split("|")
    f.close()


app = Flask(__name__)
## TODO: Create a random secure hash
app.config["SECRET_KEY"] = "notSecure"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://%s:%s@localhost/flasklogintest" % (dbUser, dbPassword)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
logging.basicConfig(filename="logg.txt", level=logging.WARNING)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
db.create_all()


@app.route('/')
@login_required
def Main():
    AvailableImages = GetAvailableImages()
    return render_template("index.html", images=AvailableImages)


@app.route('/images/<filename>')
def LoadControlImages(filename):
    return send_file("static/images/"+filename)


@app.route('/<folder>/<year>/<filename>')
def changeImage(folder, year, filename):
    global image; global deepZoomGen
    #TODO
    #add check for blank return string
    filename = FindFilenameFromList(folder, year, filename)
    str.replace(filename, "%", " ")
    path = "../../../../prosjekt/Histology/"+folder+"/"+year+"/"+filename
    print(path)
    image = openslide.OpenSlide(path)
    logger.log(25, LogFormat() + current_user.username + " requested image " + filename)

    deepZoomGen = DeepZoomGenerator(image, tile_size=254, overlap=1, limit_bounds=False)
    return deepZoomGen.get_dzi("jpeg")


@app.route('/<folder>/<year>/<dummyVariable>/<level>/<tile>')
def GetTile(folder, year, dummyVariable, level, tile):
    col, row = GetNumericTileCoordinatesFromString(tile)
    img = deepZoomGen.get_tile(int(level), (int(col), int(row)))
    return serve_pil_image(img)


@app.route('/<root>/<imageID>/<file>')
def GetDzi(root, imageID, file):
    return send_file(root+"/"+imageID+"/"+file)



def FindFilenameFromList(folder, year, filename):
    foo = allAvailableImages[folder]
    fileList = foo[year]
    for file in fileList:
        if filename in file:
            return file
    return ""


#TODO
#FOR RUNNING ON UNIX SERVER

def GetAvailableImages():
    global allAvailableImages
    for folderName1 in os.listdir("../../../../prosjekt/Histology/"):
        temp = {}
        for folderName in os.listdir("../../../../prosjekt/Histology/"+folderName1):
            if os.path.isdir("../../../../prosjekt/Histology/"+folderName1+"/"+folderName):
                listOfFiles = []
                for filename in os.listdir("../../../../prosjekt/Histology/"+folderName1+"/"+folderName):
                    if ".scn" in filename:
                        listOfFiles.append(filename)
                if listOfFiles:
                    temp[folderName] = listOfFiles
        if temp:
            allAvailableImages[folderName1] = temp
    return allAvailableImages
'''

#TODO
#FOR TESTING PURPOSES
def GetAvailableImages():
    global allAvailableImages
    allAvailableImages = {"somekey": {"2002": ["1.scn", "2.scn", "3.scn 24536.scn", "4.scn", "5.scn", "6.scn", "1.scn", "2.scn",
                                   "3.scn 24536.scn", "4.scn", "5.scn", "6.scn", "1.scn", "2.scn", "3.scn 24536.scn", "4.scn",
                                   "5.scn", "6.scn", "1.scn", "2.scn", "3.scn 24536.scn", "4.scn", "5.scn", "6.scn",
                                   "1.scn", "2.scn", "3.scn 24536.scn", "4.scn", "5.scn", "6.scn"],
                              "2003": ["1.scn", "2.scn", "3.scn 24536.scn", "4.scn", "5.scn", "6.scn", "1.scn", "2.scn",
                                   "3.scn 24536.scn", "4.scn", "5.scn", "6.scn", "1.scn", "2.scn", "3.scn 24536.scn", "4.scn",
                                   "5.scn", "6.scn", "1.scn", "2.scn", "3.scn 24536.scn", "4.scn", "5.scn", "6.scn",
                                   "1.scn", "2.scn", "3.scn 24536.scn", "4.scn", "5.scn", "6.scn"],
                              "2004": ["1.scn", "2.scn", "3.scn 24536.scn", "4.scn", "5.scn", "6.scn", "1.scn", "2.scn",
                                   "3.scn 24536.scn", "4.scn", "5.scn", "6.scn", "1.scn", "2.scn", "3.scn 24536.scn", "4.scn",
                                   "5.scn", "6.scn", "1.scn", "2.scn", "3.scn 24536.scn", "4.scn", "5.scn", "6.scn",
                                   "1.scn", "2.scn", "3.scn 24536.scn", "4.scn", "5.scn", "6.scn"],
                              "2005": ["1.scn", "2.scn", "3.scn 24536.scn", "4.scn", "5.scn", "6.scn", "1.scn", "2.scn", "3.scn 24536.scn", "4.scn", "5.scn", "6.scn", "1.scn", "2.scn", "3.scn 24536.scn", "4.scn", "5.scn", "6.scn", "1.scn", "2.scn", "3.scn 24536.scn", "4.scn", "5.scn", "6.scn", "1.scn", "2.scn", "3.scn 24536.scn", "4.scn", "5.scn", "6.scn"],
                              "2010": ["1.scn", "2.scn", "3.scn 24536.scn", "4.scn", "5.scn", "6.scn", "1.scn", "2.scn",
                                   "3.scn 24536.scn", "4.scn", "5.scn", "6.scn", "1.scn", "2.scn", "3.scn 24536.scn", "4.scn",
                                   "5.scn", "6.scn", "1.scn", "2.scn", "3.scn 24536.scn", "4.scn", "5.scn", "6.scn",
                                   "1.scn", "2.scn", "3.scn 24536.scn", "4.scn", "5.scn", "6.scn"]
                                      },
                          "someOtherKey": {
                              "2056": ["2.scn"]
                          }
                          }
    return allAvailableImages
''' 

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/images'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')



def GetNumericTileCoordinatesFromString(tile):
    col, row = str.split(tile, "_")
    row = str.replace(row, ".jpeg", "")
    return col, row


def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=80)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


# User handling methods
@app.route("/login", methods=["GET", "POST"])
def Login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user is not None and username == user.username and user.check_password(password):
            logger.log(25, LogFormat() + username + " logged in")
            login_user(user)
            return redirect("/")
        else:
            logger.log(25, LogFormat() + "Attempted loggin with username: " + username)
            return render_template("login.html", type="login", message="Wrong username or password")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
#@login_required
def Register():
    if request.method == "POST":
        registerUsername = request.form["username"]
        registerPassword = request.form["firstPassField"]

        newUser = User(registerUsername, registerPassword)
        db.session.add(newUser)
        db.session.commit()
        #logger.log(25, LogFormat() + current_user.username + " registered a new user: " + registerUsername)
        return render_template("login.html")
    else:
        return render_template("register.html")


@login_manager.user_loader
def user_login(Username):
    return User.query.get(Username)


@app.route("/logout")
@login_required
def Logout():
    logger.log(25, LogFormat() + current_user.username + " logged out")
    logout_user()
    return render_template("login.html", type="logout", message = "You are now logged out")


# Redirects users to login screen if they are not logged in.
@login_manager.unauthorized_handler
def CatchNotLoggedIn():
    return redirect("/login")


def LogFormat():
    DateTime = str(strftime("%Y-%m-%d %H:%M:%S" , gmtime()))
    ip = request.remote_addr

    return DateTime + " | " + ip + " | "

## UserMixin contains the standard methods so we dont have to implement it our self
class User(UserMixin, db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column("Username", db.String,)
    password = db.Column("Password", db.String)

    def __init__(self, usrname, password):
        self.username = usrname
        self.password = self.set_password(password)

    def set_password(self, passwrd):
        return generate_password_hash(passwrd)

    def get_password(self):
        return self.password

    def check_password(self, passwrd):
        return check_password_hash(self.password, passwrd)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, threaded=True)
