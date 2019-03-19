from time import gmtime, strftime
from flask import send_file, request
from io import BytesIO
from datetime import timedelta


def ReadDatabaseCredentialsFromFile():
    with open("Login.txt", 'r') as f:
        user, password = f.readline().split("|")
        f.close()
    return user, password


def ReadSecretKeyFromFile():
    with open("SecretKey.txt", 'r') as f:
        key = f.readline()
        f.close()
    return key


def LogFormat():
    DateTime = str(strftime("%Y-%m-%d %H:%M:%S" , gmtime()))
    ip = request.remote_addr
    return DateTime + " | " + ip + " | "


def GetNumericTileCoordinatesFromString(tile):
    col, row = str.split(tile, "_")
    row = str.replace(row, ".jpeg", "")
    return col, row


def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=80)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


def ConfigureApp(app):
    dbUser, dbPassword = ReadDatabaseCredentialsFromFile()
    ## TODO: Create a random secure hash
    app.config["SECRET_KEY"] = ReadSecretKeyFromFile()
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://%s:%s@mysql2.ux.uis.no/dbthomaso" % (dbUser, dbPassword)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.permanent_session_lifetime = timedelta(seconds=15)

