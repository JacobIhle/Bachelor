from time import gmtime, strftime
from datetime import timedelta
from flask import request


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


def ConfigureApp(app):
    dbUser, dbPassword = ReadDatabaseCredentialsFromFile()
    app.config["SECRET_KEY"] = ReadSecretKeyFromFile()
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://%s:%s@mysql2.ux.uis.no/dbthomaso" % (dbUser, dbPassword)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.permanent_session_lifetime = timedelta(minutes=75)

