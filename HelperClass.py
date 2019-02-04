from time import gmtime, strftime
from flask import Flask, send_file, render_template, send_from_directory, redirect, request, url_for
from io import BytesIO


def ReadDatabaseCredentialsFromFile():
    with open("Login.txt", 'r') as f:
        user, password = f.readline().split("|")
        f.close()
    return user, password


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
    app.config["SECRET_KEY"] = "notSecure"
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://%s:%s@localhost/flasklogintest" % (dbUser, dbPassword)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
