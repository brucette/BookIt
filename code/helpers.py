""" Helper functions for booking system """
from functools import wraps
from flask import redirect, render_template, session # type: ignore
from operator import itemgetter
import sqlite3
import datetime

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