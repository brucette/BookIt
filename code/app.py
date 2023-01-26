""" A flask based booking system with multi user support """
import sqlite3
import calendar
import datetime
import time
from os.path import exists
from flask import Flask, redirect, render_template, session, request
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required

# Configure application
app = Flask(__name__)
# app.run(debug = True)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

DB_FILE_PATH = '/code/database.db'

# Global variables
timeslots = ["10:30 - 13:30", "14:00 - 17:30", "18:30 - 23:00"]
currently = datetime.date.today()
current_year = currently.year
today = currently.day
current_month_number = currently.month

def get_db():
    """ Returns a sqlite3 db session"""
    return sqlite3.connect(DB_FILE_PATH)


def __init_db(database_path):                                      
    """Create database schema if application is started for the first time""" 
    if exists(database_path):                                      
        return   

    db_connection = get_db()
    cursor = db_connection.cursor()
    users_table = "CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
            email TEXT NOT NULL,\
            hash TEXT NOT NULL,\
            first_name TEXT NOT NULL,\
            last_name TEXT NOT NULL, \
            apartment INT NOT NULL)"

    bookings_table = "CREATE TABLE user_bookings (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
            email TEXT NOT NULL, \
            booking_time TEXT NOT NULL, \
            booking_date TEXT NOT NULL)"

    cursor.execute(users_table)
    cursor.execute("CREATE UNIQUE INDEX email ON users(email)")
    cursor.execute(bookings_table)

    db_connection.commit()
    db_connection.close()


@app.route('/dates/page/', defaults={'page': 1})
@app.route('/dates/page/<int:page>')
def dates(page):
    """ Shows calendar"""

    monthName = currently.strftime("%B")
    next_month_number = 0
    third_month_number = 0
    year = current_year

    if current_month_number < 11:
        next_month_number = current_month_number + 1
        third_month_number = current_month_number + 2
    elif current_month_number == 11:
        next_month_number = current_month_number + 1
        third_month_number = 1
    elif current_month_number == 12:
        next_month_number = 1
        third_month_number =  next_month_number + 1
    
    month1 = calendar.monthcalendar(year, current_month_number)
    month2 = calendar.monthcalendar(year, next_month_number)
    month3 = calendar.monthcalendar(year, third_month_number)
    month = month1
 
    if page == 2:
      month=month2
      monthName = calendar.month_name[next_month_number]
    elif page == 3:
      month=month3
      monthName = calendar.month_name[third_month_number]

    return render_template("calendar.html",
                           page=page,
                           today=today,
                           monthName=monthName,
                           year=year,
                           month=month,
                           current_month_number=current_month_number)


@app.route('/middle', methods=["GET", "POST"])
def middle():
    """Page to allow time for storage of selected day"""
    return render_template("middle.html")


@app.route('/dayview', methods=["GET", "POST"])
def dayview():
    """Presents available timeslots for a particular day"""

    selected_date = request.form.get("selectedDay")

    # Get today's date
    todays_date = str(today) + '/' + str(current_month_number) + '/' + str(current_year)

    # Get current time
    # t = time.localtime()
    # current_time = time.strftime("%H:%M", t)

    # Get all made bookings from this point onwards
    db_connection = get_db()
    query = f'SELECT * FROM user_bookings WHERE booking_date>="{todays_date}"'
    result = db_connection.execute(query)
    bookings = result.fetchall()

    # Commit the command
    db_connection.commit()

    # Close the connection
    db_connection.close()

    # Empty list for adding timeslot types
    timeslot_taken = []

    for timeslot in timeslots:
        for item in bookings:
            if item[3] == selected_date and item[2] == timeslot:
                timeslot_taken.append([timeslot, True])
                break
        else:
            timeslot_taken.append([timeslot, False])

    return render_template("dayview.html", 
                            timeslot_taken=timeslot_taken)


@app.route('/confirm', methods=["GET", "POST"])
def confirm():
    """Confirm booking"""
    if request.method == "GET":
        return render_template("confirm.html")

    booking_time = request.form.get("confirmTime")
    booking_date = request.form.get("confirmDay")
    current_user = session["user_id"]

    # Insert booking into users booking table:

    db_connection = get_db()

    query1 = f'SELECT email FROM users WHERE id="{session["user_id"]}"'
    result = db_connection.execute(query1)
    email = result.fetchone()

    # Insert the new booking into the bookings table
    cursor_obj3 = db_connection.cursor()
    query3 = f'INSERT INTO user_bookings (email, \
            booking_time, booking_date) VALUES ("{email}", "{booking_time}", "{booking_date}")'
    cursor_obj3.execute(query3)

    # Commit the command
    db_connection.commit()

    # Close the connection
    db_connection.close()

    return render_template("confirmed.html",
            booking_time=booking_time,
            booking_date=booking_date,
            current_user=current_user,
            email=email)


@app.route("/")
# @login_required
def index():
    """Renders landing page of the booking system"""

    return render_template("index.html")


@app.route("/welcome")
@login_required
def welcome():
    """ Once logged in greet user with this page"""
    # Query database for user's name
    db_connection = get_db()
    query = f'SELECT first_name FROM users WHERE id="{session["user_id"]}"'
    result = db_connection.execute(query)
    user = result.fetchone()

    db_connection.close()
    return render_template("index.html", user=user)


# LOGIN ROUTE
@app.route("/login", methods=["GET", "POST"])
def login():
    """Login user"""

    #Forget any user-id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        #Ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for email
        db_connection = get_db()
        query = f'SELECT * FROM users WHERE email="{request.form.get("email")}"'
        result = db_connection.execute(query)
        rows = result.fetchall()

        # Close the connection
        db_connection.close()

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("invalid email and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

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
    return redirect("/")


# REGISTER ROUTE
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Display a form so they can register
    if request.method == "GET":
        return render_template("register.html")

    # Check for possible errors
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
        db_connection = get_db()

        # Create cursor object
        cursor_obj = db_connection.cursor()

        query = f'INSERT INTO users (hash, email, first_name, last_name, apartment) \
                VALUES ("{hash_password}", "{email}", "{first_name}", "{last_name}", "{apartment}")'

        cursor_obj.execute(query)

        # Commit the command
        db_connection.commit()

        # Close the connection
        db_connection.close()
    except ValueError:
        db_connection.close()
        return apology("email is already registered")
    else:
        db_connection = get_db()
        query = f'SELECT id FROM users WHERE email="{email}"'
        result = db_connection.execute(query)
        session["user_id"] = result.fetchone()
        db_connection.close()

        # Redirect user to home page
        return redirect("/welcome")


@app.route('/confirmed')
@login_required
def confirmed():
    """ Show confirmation page for booking details """
    return render_template("confirmed.html")


@app.route('/userpage', methods=["GET", "POST"])
def userpage():
    """ Show a users bookings """

    if request.method == "POST":
        selected_row = request.form.get("selectedRow")

        db_connection = get_db()
        query = f'DELETE FROM user_bookings WHERE id="{selected_row}"'
        result = db_connection.execute(query)
        #email = result.fetchone()

        # Commit the command
        db_connection.commit()

        # Close the connection
        db_connection.close()

    db_connection = get_db()
    # Get users email
    query1 = f'SELECT email FROM users WHERE id="{session["user_id"]}"'
    result1 = db_connection.execute(query1)
    email = result1.fetchone()

    # Get users bookings
    query2 = f'SELECT * FROM user_bookings WHERE email="{email}"'
    result2 = db_connection.execute(query2)
    bookings = result2.fetchall()

    # Commit the command
    db_connection.commit()

    # Close the connection
    db_connection.close()

    currently = datetime.date.today()
    today = str(currently.day)
    month = str(currently.month)
    year = str(currently.year)
    current_date = today + "/" + month + "/" + year

    return render_template("bookings.html",
                           current_date=current_date,
                           bookings=bookings,
                           today=today,
                           month=month,
                           year=year)

                           
__init_db(DB_FILE_PATH)
app.run(host='0.0.0.0')

# CREATE TABLE user_bookings (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, email TEXT NOT NULL, booking_time TEXT NOT NULL, booking_date TEXT NOT NULL)