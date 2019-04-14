from flask import render_template, redirect, request, abort
from flask_login import login_user, current_user
from app import db, logger as db, logger
import HelperClass
import dbClasses


def handleLogin():
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]
        user = dbClasses.User.query.filter_by(username=username).first()
        if user is not None and username == user.username and user.check_password(password):
            logger.log(25, HelperClass.LogFormat() + username + " logged in")
            login_user(user)
            return redirect("/")
        else:
            logger.log(25, HelperClass.LogFormat() + "Attempted log in with username: " + username)
            return render_template("login.html", className = "warning", message="Wrong username or password")
    else:
        return render_template("login.html")


def handleRegister():
    if str(current_user.type) != "Admin":
        abort(401)
    if request.method == "POST" and request.form["username"].lower() is not None:
        registerUsername = request.form["username"].lower()
        firstPassField = request.form["firstPassField"]
        userType = request.form.get("userType")

        if dbClasses.User.query.filter_by(username=registerUsername).first() is not None:
            return render_template("register.html", className = "warning", message = "Username already exists.")

        if request.form["secondPassField"] != firstPassField:
            return render_template("register.html", className = "warning", message = "Passwords does not match")

        newUser = dbClasses.User(registerUsername, firstPassField, userType)
        db.session.add(newUser)
        db.session.commit()
        logger.log(25, HelperClass.LogFormat() + current_user.username + " registered a new user: " + registerUsername)
        return redirect("/")

    return render_template("register.html")