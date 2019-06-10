# Alex Giannini
# Project 1

Web Programming with Python and JavaScript
 

This folder contains my solution to project 1.

TO SET DATABASE_URL:
export DATABASE_URL=postgres://zfnfoqgctzmrwa:02993a0165095c94b9c6ea4af49cdb0321f1fa22c357527f61d9bbdbe0070857@ec2-107-20-185-27.compute-1.amazonaws.com:5432/dft9eo2gio7gno


Sessions
The application uses sessions to determine if the user is currently logged 
in. I found the explanation of sessions on tutortialspoint.com helpful.
https://www.tutorialspoint.com/flask/flask_sessions.htm

Hash
The application uses the werkzeug.security methods to hash the passwords. 
This is done in the submit_registration and check_login functions. 
it uses generate_password_hash and check_password_hash to determine 
correct info. At first I was exploring hashlib but then saw that Profs Malan 
and Yu pointed out the werkzeug.security methods on a discourse page.
https://discourse.cs50.net/t/flask-sign-up-login-log-out-flow/15627/6

General Design
My app's layout changed many times. At first I had no styling, then I started
to explore some of the bootstrap layout options. I wanted to have the search 
bar on every page, so I ended up putting the search function in a bootstrap navbar.
I decided to do this after going to Justin Bowling's section. He briefly demonstrated
an app of his, which had search in the navbar.

Requests
The application relies on "requests" to read the goodreads api. It is included in
requirements.txt


FILES
application.py:
The application is run from application.py. This contains all of the routing 
and database calls. My application also relies "requests" which is  listed in 
requirments.txt. It contains 4 helper functions (located at the bottom of the file)
clean string: uses strip() to get clean strings.
get_review_count: adds the number of reviews in "bookreview" according to bookid. 
get_average_reviews: calculates the average rating "bookreview" according to bookid.
get_row_count: determines the number of rows in the given SQL alchemy object.



layout.html:
To avoid writing redundant code, I created a template called layout.html. 
It contains the navigation bar as well as a link to the bootstrap cdn. 

For the html pages, I relied on bootstrap's built-in classes and grid system for 
spacing, coloring and layout. I found it gave me enough control to avoid creating 
my own css file.


login.html/error.html
The application only allows logged-in users to search. I created an error page, 
called error.html, which accepts a message argument and displays it to the user. 
Also, I created login.html which acts in a similar way. It displays the login prompt
with an error message (which I found more userful than just the error message).


register_page.html
This is the only page where the user can register. It adds input into the 'users' 
database. It will reject the 


seach_page.html
Once logged in, the application greets the user by their username, and gives directions
for the search.

results_page
Once a search is executed, it will display a list of the results on results_page.html. 
I used a Jinja2 for loop to traverse the results and display them. 


bookpage.html:
Bookpage.html will display any member of the book table. 
Each bookpage displays the number of reviews and average rating from the goodreads.com api.
Any existing reviews are retrieved from 'bookreviews' and any new reviews are inserted there.
To allow for new reviews, bookpage accepts the post method. 


export.py
This file contains my export program. It will populate the given databse with the 
given values. It is based off of the code shown in class (the difference is in the 
filename, the for lop and the SQL query).


TABLES
My application has 3 tables. If I had more time, I would have spent it improving on
my database design.

bookreviews
This table contains all of the reviews that users have submited. It has 5 columns:

id is an incrementing integer
username is a varchar
stars is an integer
review is a varchar
bookid is an integer

notes: My application queries bookreviews by bookid.

books
This table contains all of the searchable books. It has 5 columns

id is an incrementing integer
isbn is a varchar
title is an varchar
author is a varchar
year is an varchar

notes: I considered making year of type date, but was not able to do this in time.


users
This table contains all of the users. It contains three columns:

id is an incrementing integer
name is a varchar
password is an varchar























