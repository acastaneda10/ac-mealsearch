import os
import requests
import urllib.parse
import re

from flask import redirect, render_template, request, session, flash
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None

def fsearch(term):
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={term}"
    response = requests.get(url)
    response.raise_for_status()
    meals = response.json()['meals']
    return meals

def csearch(category):
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?c={category}"
    response = requests.get(url)
    response.raise_for_status()
    meals = response.json()['meals']
    return meals

def categories():
    url = f"https://www.themealdb.com/api/json/v1/1/list.php?c=list"
    response = requests.get(url)
    response.raise_for_status()
    meals = response.json()['meals']
    return meals

def mealdetails(id):
    url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={id}"
    response = requests.get(url)
    response.raise_for_status()
    meals = response.json()['meals']
    for meal in meals:
        meal['strInstructions'] = re.sub('(|\s)+(\d)+(\.|\))+(|\s)|(|\s)+Step+(|\s)+\d+(|\s)', '', meal['strInstructions'])
    return meals

def mealrandom():
    url = f"https://www.themealdb.com/api/json/v1/1/random.php"
    response = requests.get(url)
    response.raise_for_status()
    meals = response.json()['meals']
    meal_id = meals[0]['idMeal']
    return meal_id

def getingredients():
    url = f"https://www.themealdb.com/api/json/v1/1/list.php?i=list"
    response = requests.get(url)
    response.raise_for_status()
    meals = response.json()['meals']
    return meals

def isearch(ingredient):
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}"
    response = requests.get(url)
    response.raise_for_status()
    meals = response.json()['meals']
    return meals