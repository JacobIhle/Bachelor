from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

## UserMixin contains the standard methods so we dont have to implement it our self


class User(UserMixin):
    db = None
    id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column("Username", db.String,)
    password = db.Column("Password", db.String)

    def __init__(self, username, password, database):
        self.username = username
        self.password = self.set_password(password)
        self.db = database

    def set_password(self, password):
        return generate_password_hash(password)

    def get_password(self):
        return self.password

    def check_password(self, password):
        return check_password_hash(self.password, password)
