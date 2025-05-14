import os

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

# Create transactions table if it doesn't exist
db.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        shares INTEGER NOT NULL,
        price_per_share REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")
db.execute("CREATE INDEX IF NOT EXISTS user_id_idx ON transactions (user_id)")
db.execute("CREATE INDEX IF NOT EXISTS symbol_idx ON transactions (symbol)")


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
    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares_str = request.form.get("shares")

        if not symbol:
            return apology("must provide symbol", 400)

        if not shares_str:
            return apology("must provide number of shares", 400)

        try:
            shares = int(shares_str)
            if shares <= 0:
                return apology("shares must be a positive integer", 400)
        except ValueError:
            return apology("shares must be a positive integer", 400)

        stock = lookup(symbol)
        if not stock:
            return apology("invalid symbol", 400)

        user_id = session["user_id"]
        user_cash_rows = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = user_cash_rows[0]["cash"]

        total_cost = shares * stock["price"]

        if user_cash < total_cost:
            return apology("cannot afford shares", 400)

        # Record the transaction
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price_per_share) VALUES (?, ?, ?, ?)",
            user_id,
            stock["symbol"],
            shares,
            stock["price"],
        )

        # Update user's cash
        updated_cash = user_cash - total_cost
        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, user_id)

        flash(f"Bought {shares} share(s) of {stock['symbol']}!")
        return redirect("/")

    else:  # GET request
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


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
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide symbol", 400)

        stock = lookup(symbol)
        if not stock:
            return apology("invalid symbol", 400)

        return render_template("quoted.html", stock=stock)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("must provide username", 400)
        elif not password:
            return apology("must provide password", 400)
        elif not confirmation:
            return apology("must confirm password", 400)
        elif password != confirmation:
            return apology("passwords do not match", 400)

        try:
            hashed_password = generate_password_hash(password)
            db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                username,
                hashed_password,
            )
        except ValueError:
            return apology("username already exists", 400)

        # Log user in
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        session["user_id"] = rows[0]["id"]

        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares_str = request.form.get("shares")

        if not symbol:
            return apology("must select a symbol", 400)

        if not shares_str:
            return apology("must provide number of shares", 400)

        try:
            shares_to_sell = int(shares_str)
            if shares_to_sell <= 0:
                return apology("shares must be a positive integer", 400)
        except ValueError:
            return apology("shares must be a positive integer", 400)

        # Check how many shares the user owns
        owned_shares_rows = db.execute(
            "SELECT SUM(shares) as total_shares FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol",
            user_id,
            symbol,
        )

        if not owned_shares_rows or owned_shares_rows[0]["total_shares"] < shares_to_sell:
            return apology(f"you do not own enough shares of {symbol}", 400)

        stock = lookup(symbol)
        if not stock: # Should not happen if selected from owned stocks
            return apology("invalid symbol", 400)

        # Record sale (negative shares)
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price_per_share) VALUES (?, ?, ?, ?)",
            user_id,
            stock["symbol"],
            -shares_to_sell, # Negative for selling
            stock["price"],
        )

        # Update user's cash
        user_cash_rows = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = user_cash_rows[0]["cash"]
        sale_value = shares_to_sell * stock["price"]
        updated_cash = user_cash + sale_value
        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, user_id)

        flash(f"Sold {shares_to_sell} share(s) of {stock['symbol']}!")
        return redirect("/")

    else:
        # GET request: stocks owned by the user to populate the dropdown
        stocks_owned = db.execute(
            "SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING total_shares > 0",
            user_id,
        )
        return render_template("sell.html", stocks=stocks_owned)
