import requests
import os
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, fsearch, categories, csearch, mealdetails, mealrandom, getingredients, isearch

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///foodies.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/favorites")
@login_required
def favorites():
    user = session["user_id"]
    favorites = db.execute("SELECT * FROM favorites WHERE person_id = ?", user)
    return render_template("favorites.html", favorites=favorites)

@app.route("/add_favorite", methods=["POST"])
@login_required
def add_favorite():
    user = session["user_id"]
    if request.method == "POST":
        meal_id = request.form.get("id")
        meal_name = request.form.get("meal_name")
        check = len(db.execute("SELECT * FROM favorites WHERE person_id = ? AND meal_id = ?", user, meal_id)) == 1
        if check:
            flash(f"{meal_name} already in favorites!")
        else:
            db.execute("INSERT INTO favorites (person_id, meal_id, meal_name) VALUES (?,?,?)",user,meal_id,meal_name)
            flash(f"{meal_name} added to favorites!")
        return redirect("/favorites")

@app.route("/remove_favorite", methods=["POST"])
@login_required
def remove_favorite():
    user = session["user_id"]
    if request.method == "POST":
        meal_id = request.form.get("id")
        check = len(db.execute("SELECT * FROM favorites WHERE person_id = ? AND meal_id = ?", user, meal_id)) == 1
        if check:
            db.execute("DELETE FROM favorites WHERE person_id = ? AND meal_id = ?", user, meal_id)
            flash(f"Removed from favorites.")
        else:
            flash(f"Not in favorites.")
        favorites = db.execute("SELECT * FROM favorites WHERE person_id = ?", user)
        return redirect("/favorites")

@app.route("/search")
def searchf():
    if not request.args.get('search'):
        return render_template("search.html")
    else:
        search_text = request.args.get('search')
        meals = fsearch(search_text)
        return render_template("search.html", meals = meals)
    return render_template("index.html")

@app.route("/categories")
def searchc():
    cats = categories()
    if not request.args.get('search'):
        return render_template("category.html", cats = cats)
    else:
        meals = csearch(request.args.get('search'))
        return render_template("category.html", meals = meals, cats = cats)

@app.route("/details")
def details():
    meals = mealdetails(request.args.get('id'))
    return render_template("details.html", meals = meals)

@app.route("/random")
def randommeal():
    meal_id = mealrandom()
    return redirect(f"/details?id={meal_id}")

@app.route("/ingredients")
def ingredients():
    if not request.args.get('search'):
        ingredients = getingredients()
        return render_template('ingredients.html', ingredients = ingredients)
    else:
        meals = isearch(request.args.get('search'))
        return render_template("search.html", meals = meals)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        username = request.form.get("username")

        if not request.form.get("username"):
            return apology("must provide username", 400)
        if not request.form.get("password"):
            return apology("must provide password", 400)
        if not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        elif len(db.execute("SELECT username FROM users WHERE username = ?", username))>0:
            return apology("existing user found", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation do not match", 400)

        else:
            hash = generate_password_hash(request.form.get("password"),method='pbkdf2:sha256', salt_length=8)
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?);", username, hash)
            flash("Registered!")
            return redirect("/")

    else:
        return render_template("register.html")
