from flask import Flask, redirect, render_template, session, request, g, flash, url_for
from flask_session import Session
import sqlite3 
import calendar
import datetime
import time
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup

# Configure application
app = Flask(__name__)
# app.run(debug = True)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

DATABASE = '/code/database.db'

print("week days in row:", calendar.weekheader(3))
print("number of first weekday, 0:", calendar.firstweekday())
print("calendar.month:", calendar.month(2022, 12))
print("calendar.monthcalendar:", calendar.monthcalendar(2022, 12))
print("calendar.calendar", calendar.calendar(2022))
day_of_the_week = calendar.weekday(2022, 12, 9)
print("calendar.weekday", day_of_the_week)
is_leap = calendar.isleap(2020)
print("isleap", is_leap)
print(calendar.month(2020, 12, 4)) 

def get_db():
    # db = getattr(g, '_database', None)
    # if db is None:
    db = sqlite3.connect(DATABASE)
    return db


@app.route('/dates')
def dates():
    currently = datetime.datetime.now()
    month = currently.strftime("%B")
    year = currently.year
    dates = calendar.monthcalendar(year, currently.month)
    return render_template("calendar.html", month=month, year=year, dates=dates)

@app.route('/dayview')
def dayview():
    timeslots = ["10:30 - 13:30", "14:00 - 17:30", "18:30 - 23:00"]
    return render_template("dayview.html", timeslots=timeslots)

@app.route("/")
# @login_required
def index():
    return render_template("index.html")

@app.route("/welcome")
@login_required
def welcome():
    return render_template("welcome.html")

# LOGIN ROUTE
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    #Forget any user-id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        #Ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for email
        db = get_db()
        query = f'SELECT * FROM users WHERE email="{request.form.get("email")}"'
        result = db.execute(query) 
        rows = result.fetchall()
        
        # Close the connection
        db.close()

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("invalid email and/or password", 403)
       
        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        #   flash('You are now logged in')

          # Redirect user to home pgae
        return redirect("/welcome")
    
    # User reached route via GET (as by clicking a link or via redirect)
    else: 
        return render_template("login.html")

# LOGOUT ROUTE
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

# REGISTER ROUTE
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Display a form so they can register
    if request.method == "GET":
        return render_template("register.html")

    # Check for possible errors
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        verify_password = request.form.get("confirmation")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        apartment = request.form.get("apartment")

        data = [email, password, first_name, last_name, apartment]

        # for i in data:
        #     if not i:
        #         return apology('must provide {i}')

        # Ensure email was submitted
        if not email:
            return apology("must provide email")

        # # Ensure password was submitted
        if not password:
            return apology("must provide password")

        # Ensure password matches verification
        if not verify_password or password != verify_password:
            return apology("password must match verification")

        # # Ensure first name was submitted
        if not first_name:
            return apology("must provide first name")

        # # Ensure last name was submitted
        if not last_name:
            return apology("must provide last name")

        # # Ensure apartment number was submitted
        if not apartment:
            return apology("must provide apartment number")

    print(password)
    hash_password = generate_password_hash(password)
    print("hash is", hash_password)

    # Insert new user into USERS table
    try:
        # Ensure email not already registered
        # db.execute("INSERT INTO users (email, hash) VALUES (?, ?)", email, hash_password)
        db = get_db() 

        # Create cursor object
        cursor_obj = db.cursor()

        query = f'INSERT INTO users (hash, email, first_name, last_name, apartment) VALUES ("{hash_password}", "{email}", "{first_name}", "{last_name}", "{apartment}")'

        print(query)

        cursor_obj.execute(query)

        # Commit the command
        db.commit()

        # Close the connection
        db.close()
    except ValueError:
        db.close()
        return apology("email is already registered")
    else:
        db = get_db()
        #cursor_obj = db.cursor()
        query = f'SELECT id FROM users WHERE email="{email}"'
        result = db.execute(query)
        session["user_id"] = result.fetchall()
        db.close()

        # Redirect user to home page
        return redirect("/welcome")


@app.route('/confirmed')
def confirmed():
    return 'Your booking was made'

@app.route('/userpage')
def userpage():
    return 'Show users old and upcoming bookings in separate lists'

app.run(host='0.0.0.0')


# CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, email TEXT NOT NULL, hash TEXT NOT NULL, apartment NUMERIC NOT NULL);
# CREATE UNIQUE INDEX email ON users(email);
# CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, email TEXT NOT NULL, hash TEXT NOT NULL, first_name TEXT NOT NULL, last_name TEXT NOT NULL, apartment INT NOT NULL);