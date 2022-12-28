from flask import Flask, redirect, render_template, session, request, g, flash, url_for
from flask_session import Session
import sqlite3
import calendar
import datetime
import time
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup
from os.path import exists 

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

def get_db():
    return sqlite3.connect(DATABASE)

print(calendar.month(2020, 12, 4)) 
print('TODAY:', datetime.date.today())
print('TODAY:', datetime.datetime.day)
cal= calendar.Calendar()
#print('YEARDATES:', cal.yeardatescalendar(2022))

timeslots = ["10:30 - 13:30", "14:00 - 17:30", "18:30 - 23:00"]


def __init_db(DATABASE):                                      
    """Create database schema if application is started for the first time""" 
    if exists(DATABASE):                                      
        return   

    db = get_db()
    cursor = db.cursor()
    create_users_table = "CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
            email TEXT NOT NULL,\
            hash TEXT NOT NULL,\
            first_name TEXT NOT NULL,\
            last_name TEXT NOT NULL, \
            apartment INT NOT NULL)"

    cursor.execute(create_users_table)

    cursor.execute("CREATE UNIQUE INDEX email ON users(email)")

    create_bookings_table = "CREATE TABLE user_bookings (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
            email TEXT NOT NULL, \
            booking_time TEXT NOT NULL, \
            booking_date TEXT NOT NULL)"
    cursor.execute(create_bookings_table)

    db.commit()
    db.close()


@app.route('/dates')
def dates():
    currently = datetime.date.today()
    today = currently.day
    month = currently.strftime("%B")
    year = currently.year
    dates = calendar.monthcalendar(year, currently.month)
    return render_template("calendar.html", today=today, month=month, year=year, dates=dates)

@app.route('/dayview')
def dayview():
    return render_template("dayview.html", timeslots=timeslots)

@app.route('/confirm', methods=["GET", "POST"])
def confirm():
    if request.method == "GET":
      return render_template("confirm.html")
    
    booking_time = request.form.get("confirmTime")
    booking_date = request.form.get("confirmDay")
    current_user = session["user_id"]

    # Insert booking into users booking table:

    db = get_db()

    query1 = f'SELECT email FROM users WHERE id="{session["user_id"]}"'
    result = db.execute(query1)
    email = result.fetchone()

    # Insert the new booking into the bookings table
    cursor_obj3 = db.cursor()
    query3 = f'INSERT INTO user_bookings (email, booking_time, booking_date) VALUES ("{email}", "{booking_time}", "{booking_date}")'
    cursor_obj3.execute(query3)
    
    # Commit the command
    db.commit()

    # Close the connection
    db.close()

    return render_template("confirmed.html", booking_time=booking_time, booking_date=booking_date, current_user=current_user, email=email)    

@app.route("/")
# @login_required
def index():
    return render_template("index.html")

@app.route("/welcome")
@login_required
def welcome():
    # Query database for user's name
    db = get_db()
    query = f'SELECT first_name FROM users WHERE id="{session["user_id"]}"'
    result = db.execute(query)
    user = result.fetchone()
    
    # Close the connection
    db.close()
    return render_template("welcome.html", user=user)

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

    hash_password = generate_password_hash(password)

    # Insert new user into USERS table
    try:
        # Ensure email not already registered
        db = get_db()

        # Create cursor object
        cursor_obj = db.cursor()

        query = f'INSERT INTO users (hash, email, first_name, last_name, apartment) VALUES ("{hash_password}", "{email}", "{first_name}", "{last_name}", "{apartment}")'

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
        query = f'SELECT id FROM users WHERE email="{email}"'
        result = db.execute(query)
        session["user_id"] = result.fetchall()
        db.close()

        # Redirect user to home page
        return redirect("/welcome")


@app.route('/confirmed')
@login_required
def confirmed():
    return render_template("confirmed.html")

@app.route('/userpage')
def userpage():
    # Get all of users bookings

    db = get_db()
    # Get users email
    query1 = f'SELECT email FROM users WHERE id="{session["user_id"]}"'
    result1 = db.execute(query1)
    email = result1.fetchone()

    # Get users bookings
    query2 = f'SELECT * FROM user_bookings WHERE email="{email}"'
    result2 = db.execute(query2)
    bookings = result2.fetchall()

    # Commit the command
    db.commit()

    # Close the connection
    db.close()

    currently = datetime.date.today()
    today = str(currently.day)
    month = str(currently.month)
    year = str(currently.year)
    current_date = today + "/" + month + "/" + year

    # current_time = datetime.datetime.now().strftime("%H:%M:%S")

    return render_template("bookings.html", current_date=current_date, bookings=bookings, today=today, month=month, year=year)

__init_db(DATABASE)
app.run(host='0.0.0.0')



# CREATE UNIQUE INDEX email ON users(email);
# CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, email TEXT NOT NULL, hash TEXT NOT NULL, first_name TEXT NOT NULL, last_name TEXT NOT NULL, apartment INT NOT NULL);
# 