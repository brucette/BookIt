# BookIt
#### Video Demo:  <URL HERE>
#### Description:

BookIt is a a web-based application that residents of an apartment complex can use to 
book a timeslot to hold social events in their communal area .

Users of the app can register for an account or login, view available times (curently only
for the following 3 months), make a booking, view their own bookings or all the bookings 
in the system, and cancel any of their upcoming bookings.

The idea came to me when I saw a simple piece of paper was currently used for 
this purpose in the apartment building I live in, and thought it might be more convenient 
to be able to see the available times without having to go to the location each time one 
wanted to use the communal area. 

Micro web-framework **Flask**  is used to build the 
project. 

**Python** is used in _app.py_ to configure the application, connect it to a **Sqlite3** database 
file, create all the needed tables (users and user_bookings) upon initialization and to define the 
different routes accessible by the application. 

Sqlite3 is used as the database to store user data upon registering and for storing all the 
bookings that are made.

The templates-folder contains the **HTML** files that are rendered with the help of
**Jinja templating laguage** once the user accesses the different routes of the app:
 
 -  _layout.html_ - contains the nav bar and the skeleton of the website, contains the placeholders 
 (block title and block main) for information from the other html files to rendered into, and displayed on the browser. 
 E.g. the block title "Bookings" and the block main which is the list of all the bookings in the database, are rendered via the layout file when the user goes to the /userpage path of the website.
 -  _index_ - landing page
 -  _register_ - displays a form for registering
 -  _login_ - displays a form for registering
 -  _apology_ - rendered when user forgets to include any form item in register or loging form
 -  _bookings_ - lists all bookings with a button to select only logged in user's bookings
 -  _calendar_ - displays all days for current month with buttons to move to the next two months
 -  _dayview_ - displays all 3 timeslots available per day, available timeslot is an active, clickable button and an unavailable one is a deactive, unclickable button. 
 -  _middle_ - a page that is briefly rendered, to allow time for the date user has selected and to post it to the backend to retrieve and show available timeslots for that day. 
 -  _confirm_ - displays the selected date and time of the booking user has chosen with a button to confirm their choice
 -  _confirmed_ - displays a checkmark to user indicating booking has been made

 
**Javascript** is used in _script.js_ to add interactivity, mainly event listeners to various buttons throughout the site, which is styled and made to be responsive on different screen sizes using **CSS**. 