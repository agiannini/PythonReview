import os
import requests


from flask import Flask, session, render_template, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash

from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")



# CREATE DB
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))



# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



# Purpose: landing page.
# Appraoch: displays the search page with the top five seaches.
@app.route("/")
def index():
        session['username'] = '';
        topFiveRev = getTopFive();
        username = session['username']
        return render_template("search_page.html", name=username, searches=topFiveRev)




# Displays the registration page.
@app.route("/register")
def register():
    return render_template("register.html")




# Purpose: to validate the registration information.
# Appraoch: Gets info from form. If not in the table, inserts it.
@app.route("/submit_registration", methods=["POST"])
def submit_registration():
    name = request.form.get("username")
    if db.execute("SELECT * FROM users WHERE name = :name", {"name":name}).rowcount > 0:
        return render_template("register.html", registration_error="That Username Is Allready Taken. Please login Try Again!")
    password = request.form.get("password")
    enc_pword = generate_password_hash(password)
    db.execute("INSERT INTO users (name, password) VALUES (:name, :password)", {"name": name, "password": enc_pword})
    db.commit()
    session['username'] = name
    topFiveRev = getTopFive();
    return render_template("search_page.html", name=session['username'], searches=topFiveRev)




# Purpose: to log the user out of the session
# Appraoch: removes username from session and prompts for login
@app.route("/logout")
def logout():
    if 'username' not in session:
        return render_template("login.html", message="You are not logged In.")
    session.pop('username', None)
    return render_template("login.html", message="Please Login Below.")




# Purpose: to check the username password given in the form.
# Approach: Checks if user exists, retrieves encoded password, adds user to session.
@app.route("/check_login", methods=["POST"])
def check_login():
    name = request.form.get("username")
    password = request.form.get("password")
    if db.execute("SELECT * FROM users WHERE name = :name", {"name": name}).rowcount == 0:
        return render_template("login.html", message="Incorrect Username or Password! Please register or Login")
    result = db.execute("SELECT * FROM users WHERE name = :name", {"name": name}).fetchone()
    enc_pword = result.password
    if check_password_hash(enc_pword, password):
        session['username'] = name
    topFiveRev = getTopFive();
    return render_template("search_page.html", name=session['username'], searches=topFiveRev)
    return render_template("login.html", message="Incorrect Username or Password! Please register or Login")





# Purpose: to greet the user and give search instructions.
# Approach: sends username to the page for display
@app.route("/search_page", methods=["POST", "GET"])
def search_page():
    topFiveRev = getTopFive();
    return render_template("search_page.html", name=session['username'], searches=topFiveRev)



# Purpose: to display the results from the search.
# Approach: Checks if  user is looged in, then gets results from the database.
@app.route("/results_page", methods=["POST"])
def results_page():
    search = '%'+request.form.get("search")+'%'
    results = db.execute("SELECT * from books WHERE LOWER(author) LIKE LOWER(:search) OR LOWER(title) LIKE LOWER(:search) OR LOWER(isbn) LIKE LOWER(:search) OR LOWER(year) LIKE LOWER(:search) ",
        {"search": search}).fetchall()
    search = process_string(search)                                         # To display on webpage
    no_results_msg = ""
    if get_row_count(results) == 0:
        no_results_msg = "There Were No Results!"
    return render_template("results_page.html", search=search, results=results, no_results_msg=no_results_msg)





# Purpose: To display the individual book pages.
# Approach: creates variables from database, queries goodreads, sends to page
#           if method==POST allows users to submit reviews.
@app.route("/results/<int:id>", methods=["GET", "POST"])
def mybooks(id):
    results = db.execute("SELECT * from books WHERE id = :id", {"id": id}).fetchone()
    my_title = results.title
    my_author = results.author
    my_isbn = results.isbn
    my_year = results.year
    reviews = db.execute("SELECT * from bookreviews").fetchall()

    if request.method=="POST":
        if session['username'] == '':
            session['username'] = "anonymous"
        username= session['username']
        stars = request.form.get("stars")
        review = request.form.get("review")
        db.execute("INSERT INTO bookreviews (username, stars, review, bookid) VALUES (:username, :stars, :review, :bookid)",
            {"username": username, "stars": stars, "review": review, "bookid": id})
        db.commit()

    goodreads_response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "sVFO0CSWAdtk4YheNxYog", "isbns": my_isbn})
    if goodreads_response.status_code != 200:
        return render_template("error.html", message="API Request Was unsuccessful")
    data = goodreads_response.json()
    goodreads_total = data["books"][0]["ratings_count"]
    goodreads_avg = data["books"][0]["average_rating"]                                      # key "books" returns a list containing 1 object
    reviews = db.execute("SELECT * from bookreviews WHERE bookid = :my_id",
        { "my_id": id }).fetchall()
    db.commit()
    return render_template("bookpage.html", my_id=id, my_title=my_title, my_author=my_author, my_isbn=my_isbn, my_year=my_year, reviews=reviews, goodreads_total=goodreads_total, goodreads_avg=goodreads_avg)






# Purpose: To display JSON object for indicated isbn.
# Approach: creates variables from database, jsonify, sends to page
@app.route("/api/<string:isbn>", methods=["GET"])   #404
def myapi(isbn):
    if db.execute("SELECT title FROM books WHERE isbn = :isbn",{"isbn": isbn}).rowcount == 0 :
        return jsonify({"error": "Invalid ISBN Number"}), 400

    results = db.execute("SELECT * from books where isbn = :isbn", {"isbn": isbn}).fetchone()

    my_title = results.title
    my_author = results.author
    my_isbn = results.isbn
    my_year = results.year
    my_id = results.id

    review_avg = 0
    review_count = get_review_count(my_id)
    if review_count > 0:
        review_avg = get_average_reviews(my_id)/review_count

    return jsonify ({
        "title": my_title,
        "author": my_author,
        "isbn": my_isbn,
        "year": my_year,
        "review_count": review_count,
        "my_id": my_id,
        "review_avg": review_avg
    })







#get_row_count
#Purpose: to find the amount of rows in the given SQLAchelmy objects
def get_row_count(results):
    counter = 0
    for result in results:
        counter+=1
    return counter




#get_review_count
#Purpose: to retrive the average review of the given isbns
#Arguments: an int indicating the isbn Number
def get_review_count(my_id):
    review_count = db.execute("SELECT * from bookreviews WHERE bookid = :my_id",
        { "my_id": my_id }).rowcount
    return review_count



#getTopFive
#Purpose: to return the most recent five reviews
def getTopFive():
    recent  = db.execute("SELECT MAX(id) FROM bookreviews").fetchall()
    topFive = [int(x[0]) for x in recent]

    return db.execute("SELECT * FROM bookreviews WHERE id > :id", {"id":topFive[0] - 5}).fetchall()




#get_average_reviews
#Purpose: to retrive the average review of the given isbns
#Arguments: an int indicating the isbn Number
def get_average_reviews(my_id):
    reviews = db.execute("SELECT * from bookreviews WHERE bookid = :my_id",
        {"my_id": my_id}).fetchall()
    sum = 0
    for review in reviews:
        num = str(review.stars)
        num = process_string(num)
        sum += int(num)
    return sum



#process_string
# Arguments: a string
# Purpose: to remove the extra characters on converted SQLAchelmy objects
def process_string(word):
    word = word.strip('()\'\,\'\%')
    return word
