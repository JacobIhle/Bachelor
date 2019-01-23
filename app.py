#LICENSE: https://github.com/openslide/openslide/blob/master/lgpl-2.1.txt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import Flask, send_file, render_template, send_from_directory, redirect, request
from openslide.deepzoom import DeepZoomGenerator
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
import os
import openslide

image = None
deepZoomGen = None

app = Flask(__name__)
app.config["SECRET_KEY"] = "notSecure"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Moonkee1@localhost/flasklogintest"

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

## UserMixin contains the standard methods so we dont have to implement it our self
class User(UserMixin, db.Model):
    id = db.Column("UserID", db.Integer, primary_key=True)
    username = db.Column("Username", db.Unicode)
    password = db.Column("Password", db.Integer)


@login_manager.user_loader
def user_login(UserID):
    return User.query.get(int(UserID))


@app.route("/logout")
@login_required
def Logout():
    logout_user()
    return "You are now logged out"


@app.route("/home")
@login_required
def home():
    return "The current user is " + current_user.username


@app.route("/password")
@login_required
def password():
    return "The password is: " + str(current_user.password)


@app.route("/login", methods=["GET", "POST"])
def Login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        pswrd = User.query.filter_by(password=password).first()
        # Probably not the best way to do it
        # TODO: Find the correct way
        if user and pswrd is not None:
            if user == pswrd:
                login_user(user)
                return render_template("index.html")
    return render_template("login.html", user=user_login(1), )


@login_manager.unauthorized_handler
def CatchNotLoggedIn():
    return redirect("/login")

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
    image = openslide.OpenSlide("scnImages/"+filename+".scn")
    deepZoomGen = DeepZoomGenerator(image, tile_size=254, overlap=1, limit_bounds=False)
    return deepZoomGen.get_dzi("jpeg")


@app.route('/scnImages/<dummyVariable>/<level>/<tile>')
def GetTile(dummyVariable, level, tile):
    col, row = GetNumericTileCoordinatesFromString(tile)
    img = deepZoomGen.get_tile(int(level), (int(col), int(row)))
    return serve_pil_image(img)


@app.route('/<root>/<imageID>/<file>')
def GetDzi(root, imageID, file):
    return send_file(root+"/"+imageID+"/"+file)


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


if __name__ == '__main__':
    app.run(port=5000, threaded=True)
