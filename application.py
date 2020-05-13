import os 
import requests

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app) 

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    """Register"""

    # Get form information.
    name = request.form.get("id")
    passw = request.form.get("password")

    if db.execute("SELECT * FROM users WHERE id = :name", {"name": name}).rowcount > 0:
        return render_template("error.html", message="User Already Exists!!!")
    db.execute("INSERT INTO users (id, password) VALUES (:name, :password)", {"name": name, "password": passw})
    db.commit()
    return render_template("success.html")    

@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("id")
    passw = request.form.get("password")

    if db.execute("SELECT * FROM users WHERE id = :id AND password = :password", {"id": name, "password": passw}).rowcount == 0:
        return render_template("error.html", message="Invalid User ID/Password OR you might not have registered.") 
    session["userid"] = name
    return render_template("success2.html")


@app.route("/searchbook")
def searchbook():
    return render_template("success2.html")

@app.route("/search", methods=["POST"])
def search():
    isbn = request.form.get("isbnnumber")
    title = request.form.get("title")
    author = request.form.get("author")

    t = "%" + title + "%"
    i = "%" + isbn + "%"
    a = "%" + author + "%"
    if len(title) > 0:
        title2 = db.execute("SELECT title, isbn FROM books WHERE title LIKE :ti", {"ti": t}).fetchall()
        if len(title2) == 0: 
            return render_template("errorduplicatereview.html", message="Zero Books Found!!!")

        return render_template("book.html", title2=title2)

    elif len(isbn) > 0:
        isbn2 = db.execute("SELECT title, isbn FROM books WHERE isbn LIKE :i", {"i": i}).fetchall()
        if len(isbn2) == 0: 
            return render_template("errorduplicatereview.html", message="Zero Books Found!!!")

        return render_template("book.html", title2=isbn2)

    elif len(author) > 0:
        author2 = db.execute("SELECT title, isbn FROM books WHERE author LIKE :au", {"au": a}).fetchall()
        if len(author2) == 0: 
            return render_template("errorduplicatereview.html", message="Zero Books Found!!!")

        return render_template("book.html", title2=author2)
    
    else:
        return render_template("errorduplicatereview.html", message="Please enter ISBN number OR Book Title OR OR Author's Name")

@app.route("/reviewsubmit/<string:i>", methods=["POST"])
def reviewsubmit(i):
    rat = request.form.get("rating")
    rev = request.form.get("review")
    s = session["userid"]

    if db.execute("SELECT id FROM reviews WHERE id = :user AND isbn = :i", {"user": s, "i": i}).rowcount > 0:
        return render_template("errorduplicatereview.html", message="you have already submitted a review for this book.")
    else:
        db.execute("INSERT INTO reviews(id, isbn, rating, review) VALUES (:id, :isbn, :rating, :review)", {"id": s, "isbn": i, "rating": rat, "review": rev})
        db.commit()
        return render_template("success3.html")

@app.route("/apis/<string:isbn>")
def apis(isbn):
    x = db.execute("SELECT * FROM books WHERE isbn = :i", {"i": isbn}).fetchone()

    # From Goodreads getting average rating and number of ratings
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "0mTZZZX4ccutK7vkREHfzQ", "isbns": isbn})
    avg_rating_Goodreads = res.json()['books'][0]['average_rating']
    work_rating_count = res.json()['books'][0]['work_ratings_count']

    review = db.execute("SELECT id, review FROM reviews WHERE isbn = :isb", {"isb": isbn}).fetchall()
    return render_template("bookinfo.html", x=x, reviews=review, avg_gr=avg_rating_Goodreads, work_gr=work_rating_count)
    # return res.json()

@app.route("/api/<string:isbn>")
def api(isbn):
    jsonobj = {"title": "", "author": "", "year": 0, "isbn": isbn, "review_count": 0, "average_score": 0.0}

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "0mTZZZX4ccutK7vkREHfzQ", "isbns": isbn})

    jsonobj["average_score"] = res.json()['books'][0]['average_rating']
    jsonobj["review_count"] = res.json()['books'][0]['work_ratings_count']

    data = db.execute("SELECT title, author, year FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    jsonobj["title"] = data.title
    jsonobj["author"] = data.author
    jsonobj["year"] = data.year


    return jsonify(jsonobj)

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("userid", None)
    return render_template("index.html")