import os
import datetime
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    # Set the transactions database to the SQL query
    transactions_index_database = db.execute(
        "SELECT symbol, SUM(shares) as shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING shares > 0",
        user_id,
    )
    cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    cash = cash_db[0]["cash"]
    grand_total = cash
    for transaction in transactions_index_database:
        details = lookup(transaction["symbol"])
        transaction["price"] = details["price"]
        grand_total += transaction["shares"] * transaction["price"]

    return render_template(
        "index.html",
        database=transactions_index_database,
        cash=cash,
        total=grand_total,
    )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        if not request.form.get("shares").isdigit():
            return apology(" ")
        shares = int(request.form.get("shares"))
        # Make sure we have entries
        if not symbol:
            return apology("You need the symbol!")
        if not shares:
            return apology("You need the number of the shares!")
        # Test if they're valid
        stock = lookup(symbol)
        if stock == None:
            return apology("We can't find that stock- try again?")
        if shares <= 0:
            return apology("You need a positive number of shares to buy them.")
        # Check if the user can afford the purchase
        total_cost = stock["price"] * shares

        user_id = session["user_id"]
        user_cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = user_cash_db[0]["cash"]

        if user_cash < total_cost:
            return apology("You're too broke L bozo")

        # Update user's cash
        updated_cash = user_cash - total_cost
        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, user_id)
        date = datetime.datetime.now()
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price, date) VALUES (?, ?, ?, ?, ?)",
            user_id,
            stock["symbol"],
            shares,
            stock["price"],
            date,
        )
        return redirect("/")

    # If GET, go to buy.html
    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # Show all that user's transactions
    user_id = session["user_id"]
    transactions_history_db = db.execute(
        "SELECT * FROM transactions WHERE user_id = ?", user_id
    )
    return render_template("history.html", transactions=transactions_history_db)


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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()

        if not symbol:
            return apology("You'll need a symbol!")

        stock = lookup(symbol)
        if stock == None:
            return apology("That symbol doesn't exist- try again?")
        return render_template(
            "quoted.html", symbol=stock["symbol"], price=stock["price"]
        )
    # If GET, go to quote.html
    return render_template("quote.html")


def is_strong_password(password):
    """Check if the password is at least 8 characters, has at least one lowercase & uppercase letter, has at least 1 number, and has at least one symbol."""
    if len(password) < 8:
        return apology("Your password needs to be at least 8 characters!")

    # Fill variables with the relevant letters, snumbers, and symbols
    uppercase = re.compile(r"[A-Z]")
    if not uppercase.search(password):
        return apology("Your password needs to have at least one uppercase letter.")
    lowercase = re.compile(r"[a-z]")
    if not lowercase.search(password):
        return apology("Your password needs to have at least one lowercase letter.")
    number = re.compile(r"\d")
    if not number.search(password):
        return apology("Your password needs to have at least one number.")
    symbol = re.compile(r'[!@#$%^&*()_+{}|:"<>?~\[\];\',./\\`\-]')
    if not symbol.search(password):
        return apology("Your password needs to have at least one symbol.")
    # If nothing went wrong, return None
    return None


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username:
            return apology("You need a username!")
        if not password:
            return apology("You need a password!")
        if not confirmation:
            return apology("You need to confirm.")
        if password != confirmation:
            return apology("Hey! Make your passwords match!")
        password_issue = is_strong_password(password)
        if password_issue:
            return password_issue

        # Check if the username's taken
        users = db.execute("SELECT * FROM users;")
        if any(user["username"] == username for user in users):
            return apology("Username already exists, wanna pick a different one?")
        else:
            # INSERT the new user into users, storing a hash of the user’s password
            hashed_pw = generate_password_hash(password)
            new_user = db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)", username, hashed_pw
            )
            session["user_id"] = new_user
            return redirect("/")
    # If GET, go to register.html
    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))
        # Check if the entries are there
        if not symbol:
            return apology("Pick a stock!")
        if not shares:
            return apology("Enter the number of shares to sell, please!")
        # Check if the entries are valid
        stock = lookup(symbol.upper())
        if stock == None:
            return apology("Stock doesn't exist, sorry!")
        if shares < 0:
            return apology("Shares need to be positive! Try again")

        # Get the ID and the cash/shares from the database
        user_id = session["user_id"]
        user_cash_database = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = user_cash_database[0]["cash"]
        user_shares_database = db.execute(
            "SELECT shares FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol",
            user_id,
            symbol,
        )
        if user_shares_database:
            user_shares = user_shares_database[0]["shares"]
        else:
            return apology("You don't have any shares... yikes")

        if shares > user_shares:
            return apology("You don't have enough shares... awkward")

        # Update the user's cash if the sale goes through
        transaction_total = shares * stock["price"]
        new_cash = user_cash + transaction_total
        date = datetime.datetime.now()
        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, user_id)
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price, date) VALUES (?, ?, ?, ?, ?)",
            user_id,
            stock["symbol"],
            (-1) * shares,
            stock["price"],
            date,
        )
        return redirect("/")

    # If method is GET, get the user's session and then redirect to sell
    user_id = session["user_id"]
    return render_template("sell.html")
