""" A flask based booking system with multi user support """
import sqlite3
import calendar
import datetime
import time
from os.path import exists
# pylint: disable=import-error
from flask import Flask, redirect, render_template, session, request # type: ignore
from werkzeug.security import check_password_hash # type: ignore
from flask_session import Session # type: ignore
from helpers import (
  apology, login_required,
  compute_timeslot_status,
  insert_user,
  get_bookings,
  normalize_booking_dates,
  sort_bookings,
  validate_register_form
)

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

DB_FILE_PATH = '/code/database.db'

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
            last_name TEXT NOT NULL,\
            apartment INT NOT NULL)"

    bookings_table = "CREATE TABLE user_bookings (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
            email TEXT NOT NULL,\
            first_name TEXT NOT NULL,\
            apartment INT NOT NULL,\
            booking_time TEXT NOT NULL,\
            booking_date TEXT NOT NULL,\
            notes TEXT)"

    cursor.execute(users_table)
    cursor.execute("CREATE UNIQUE INDEX email ON users(email)")
    cursor.execute(bookings_table)

    db_connection.commit()
    db_connection.close()


@app.route("/")
def index():
    """Renders landing page of the booking system"""
    return render_template("index.html")


# REGISTER ROUTE
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "GET":
        return render_template("register.html")

    values, error = validate_register_form(request.form)

    if error:
        return apology(error)

    user_id, user_name, error = insert_user(values)

    session["user_id"] = user_id
    session["user_name"] = user_name

    return redirect("/welcome")


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
        session["user_name"] = rows[0][3]

        # Redirect user to home pgae
        return redirect("/welcome")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@app.route("/welcome")
@login_required
def welcome():
    """ Once logged in greet user with this page"""
    return render_template("index.html")


@app.route('/dates/page/', defaults={'page': 1})
@app.route('/dates/page/<int:page>')
@login_required
def dates(page):
    """ Shows calendar"""

    currently = datetime.date.today()
    current_year = currently.year
    today = currently.day
    current_month_number = currently.month

    month_name = currently.strftime("%B")
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
        month_name = calendar.month_name[next_month_number]
    elif page == 3:
        month=month3
        month_name = calendar.month_name[third_month_number]

    return render_template("calendar.html",
                           page=page,
                           today=today,
                           month_name=month_name,
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

    # Convert selected date into a datetime date to make comparing and sorting possible
    comp_date = datetime.datetime.strptime(selected_date, "%d/%m/%Y").date()

    today = datetime.date.today()
    todays_date = f"{today.day}/{today.month}/{today.year}"
    current_time = time.strftime("%H:%M", time.localtime())

    bookings = get_bookings()

    # Replace dates in booking with a datetime date to make sorting possible
    new_bookings_list = normalize_booking_dates(bookings)

    # Empty list for adding timeslot types
    timeslot_taken = compute_timeslot_status(
        new_bookings_list, comp_date,selected_date, todays_date, current_time)

    return render_template("dayview.html",
                            todays_date=todays_date,
                            current_time=current_time,
                            selected_date=selected_date,
                            bookings=bookings,
                            timeslot_taken=timeslot_taken)


@app.route('/confirm', methods=["GET", "POST"])
def confirm():
    """Confirm booking"""
    if request.method == "GET":
        return render_template("confirm.html")

    booking_time = request.form.get("confirmTime")
    booking_date = request.form.get("confirmDay")
    notes = request.form.get("notes")
    current_user = session["user_id"]

    # Insert booking into users booking table:

    db_connection = get_db()

    query1 = f'SELECT email, first_name, apartment FROM users WHERE id="{session["user_id"]}"'
    result = db_connection.execute(query1)
    identifiers = result.fetchall()
    email = identifiers[0][0]
    first_name = identifiers[0][1]
    apartment = identifiers[0][2]

    # Insert the new booking into the bookings table
    cursor_obj3 = db_connection.cursor()
    query3 = f'INSERT INTO user_bookings (email, \
            first_name, apartment, booking_time, booking_date, notes) \
            VALUES ("{email}", \
                    "{first_name}", \
                    "{apartment}", \
                    "{booking_time}", \
                    "{booking_date}", \
                    "{notes}")'
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


@app.route('/confirmed')
@login_required
def confirmed():
    """ Show confirmation page for booking details """
    return render_template("confirmed.html")


@app.route('/userpage', methods=["GET", "POST"])
def userpage():
    """ Show bookings """

    db_connection = get_db()

    # Get users email, name and apartment number
    query1 = f'SELECT email FROM users WHERE id="{session["user_id"]}"'
    result1 = db_connection.execute(query1)
    identifiers = result1.fetchall()
    email = identifiers[0][0]

    all_bookings = sort_bookings(normalize_booking_dates(get_bookings()))

    # Commit the command
    db_connection.commit()

    # Close the connection
    db_connection.close()

    # Filter the new_bookings_list to only include current user's bookings
    user_bookings = [b for b in all_bookings if b[1] == email]

    current_date = datetime.date.today()
    today = str(current_date.day)

    show = all_bookings

    if request.method == "POST":
        selected_row = request.form.get("selectedRow")
        select_bookings = request.form.get("select_bookings")

        if selected_row:
            db_connection = get_db()
            query = f'DELETE FROM user_bookings WHERE id="{selected_row}"'
            db_connection.execute(query)
            db_connection.commit()
            db_connection.close()

        if select_bookings:
            show = all_bookings if select_bookings == "All bookings" else user_bookings

    return render_template("bookings.html",
                           show=show,
                           current_date=current_date,
                           today=today)


# LOGOUT ROUTE
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


__init_db(DB_FILE_PATH)
app.run(host='0.0.0.0')

# CREATE TABLE user_bookings (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, email TEXT NOT NULL,
# first_name TEXT NOT NULL, apartment INT NOT NULL, booking_time TEXT NOT NULL,
# booking_date TEXT NOT NULL, notes TEXT);
