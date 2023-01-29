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

**Python** is used in app.py to configure the application, connect it to an **Sqlite3** database file, create all the needed tables (users and user_bookings) upon initialization and to define the 
different routes accessible by the application. 

The templates-folder contains the various **HTML** files that are rendered with the help of
**Jinja templating laguage** once the user accesses the different routes of the app: 

Sqlite3 is used as the database to store user data upon registering and for storing all the 
bookings that are made. 
Javascript is used to add interactivity, mainly event listeners to various buttons throughout
the site. 
The site is styled and made responsive with CSS. 

Technologies used: 
Python,
Sqlite3,
Flask, 
Jinja templating language,
Javascript,
Responsive,
HTML, 
CSS,
Docker - to build an image,