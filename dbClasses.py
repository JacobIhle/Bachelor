from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db as db


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