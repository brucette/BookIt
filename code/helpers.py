""" Helper functions for booking system """
from functools import wraps
# pylint: disable=import-error
from operator import itemgetter
import sqlite3
import datetime
from flask import redirect, render_template, session # type: ignore
from werkzeug.security import generate_password_hash # type: ignore

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

def validate_register_form(form):
    """ Validate registration form and return cleaned values. """
    form_fields = {
        "email": "Email",
        "password": "Password",
        "confirmation": "Confirmation",
        "first_name": "First name",
        "last_name": "Last name",
        "apartment": "Apartment number"
    }

    values = {}
    for field, display_name in form_fields.items():
        value = form.get(field)
        if not value:
            return None, f"Must provide {display_name.lower()}"
        values[field] = value

    if values["password"] != values["confirmation"]:
        return None, "Password must match verification"

    return values, None

def insert_user(values):
    """ Insert a new user and return user id and name. """

    hash_password = generate_password_hash(values["password"])

    db_connection = get_db()
    cursor_obj = db_connection.cursor()

    try:
        cursor_obj.execute(
        f'INSERT INTO users (hash, email, first_name, last_name, apartment) '
        f'VALUES ("{hash_password}", "{values["email"]}", "{values["first_name"]}", '
        f'"{values["last_name"]}", "{values["apartment"]}")'
    )

        db_connection.commit()
    except sqlite3.IntegrityError:
        db_connection.close()
        return None, None, "Email is already registered"
    finally:
        db_connection.close()

    db_connection = get_db()
    query = f'SELECT * FROM users WHERE email="{values["email"]}"'
    result = db_connection.execute(query)
    row = result.fetchone()
    db_connection.close()

    return row[0], row[3], None

def get_db():
    """ Returns a sqlite3 db session"""
    return sqlite3.connect('/code/database.db')

def get_bookings():
    """ Fetch all bookings from the database as mutable lists. """
    db = get_db()
    result = db.execute('SELECT * FROM user_bookings')
    bookings = result.fetchall()
    db.commit()
    db.close()
    return [list(item) for item in bookings]

def normalize_booking_dates(bookings):
    """ Convert booking date strings (index 5) to datetime.date objects. """
    for booking in bookings:
        booking[5] = datetime.datetime.strptime(booking[5], "%d/%m/%Y").date()
    return bookings

def compute_timeslot_status(new_bookings_list, comp_date,selected_date, todays_date, current_time):
    """
    Determine the availability of each timeslot for a given day.

    Checks whether each timeslot is already booked or, if the day is today,
    whether the timeslot has already passed. """
    timeslots = ["10:30 - 13:30", "14:00 - 17:30", "18:30 - 23:00"]
    timeslot_taken = []

    # Check whether date and time already taken
    for timeslot in timeslots:
        for item in new_bookings_list:
            if item[5] == comp_date and item[4] == timeslot:
                timeslot_taken.append([timeslot, True])
                break
            if selected_date == todays_date and current_time > timeslot:
                timeslot_taken.append([timeslot, True])
                break
        else:
            timeslot_taken.append([timeslot, False])

    return timeslot_taken

def sort_bookings(bookings):
    """Sort bookings by date and time descending."""
    bookings.sort(key=itemgetter(5, 4), reverse=True)
    return bookings
