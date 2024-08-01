import sqlite3
from helpers import create_sqlite_database, login_required
from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

create_sqlite_database("library.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods = ["GET", "POST"])
@login_required
def index():
    """Home Page"""

    cash = session["cash"]
    conn = sqlite3.connect("library.db")
    db = conn.cursor()

    # If request is POST, get the details of the selected book and render the buy_book template with these details
    if request.method == "POST":
        id = request.form.get("book_id")

        db.execute("SELECT title, author, price FROM books WHERE id = ?", (id,))
        book = db.fetchall()[0]
        title = book[0]
        author = book[1]
        price = book[2]

        conn.close()
        return render_template("buy_book.html", id=id, title=title, author=author, price=price, cash=cash)
    
    # If request is GET, get the list of books in the books table that belong tho the admin
    else:
        db.execute("SELECT id, title, author, COUNT(title), price FROM books WHERE user_id = 1 GROUP BY title ORDER BY title")
        books = db.fetchall()

        conn.close()
        return render_template("index.html", books=books, cash=cash)


@app.route("/register", methods = ["GET", "POST"])
def register():
    """Register new user"""
    session.clear()

    # If request is POST, get valid username and password and register user
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if user provided a username
        if not username:
            flash("Please provide a username")
            return render_template("register.html")
        
        conn = sqlite3.connect("library.db")
        db = conn.cursor()
        db.execute("SELECT * FROM users WHERE username = ?", (username,))
        rows = db.fetchall()
        
        # Check if username is taken
        if len(rows) != 0:
            flash("Username is already exists")
            return render_template("register.html")

        # Check if user provided a password
        if not password:
            flash("Please provide a password")
            return render_template("register.html")
        
        if len(password) < 10:
            flash("Password must be at least 10 characters wide")
            return render_template("register.html")

        # Check if user provided a password confirmation
        if not confirmation:
            flash("Please confirm password")
            return render_template("register.html")
        
        # Check if password matches the password confirmation
        if password != confirmation:
            flash("Passwords do not match")
            return render_template("register.html")
        
        # Generate a hash for the user's password
        hash = generate_password_hash(password)

        # Add the user to the database
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash))
        conn.commit()

        db.execute("SELECT id, cash FROM users WHERE username = ?", (username,))
        user = db.fetchall()

        # Remember the user
        session["user_id"] = user[0][0]
        session["cash"] = user[0][1]

        conn.close()
        return redirect("/")

    # if request is GET, render the register template
    else:
        return render_template("register.html")


@app.route("/login", methods = ["GET", "POST"])
def login():
    """User log in"""
    session.clear()

    # If request is POST, get valid username and password
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if user provided a username
        if not username:
            flash("Please provide a username")
            return render_template("login.html")
        
        # Check if user provided a password
        if not password:
            flash("Please provide a password")
            return render_template("login.html")
        
        conn = sqlite3.connect("library.db")
        db = conn.cursor()
        db.execute("SELECT * FROM users WHERE username = ?", (username,))
        rows = db.fetchall()

        # Check if username and password match a user
        if len(rows) != 1 or not check_password_hash(rows[0][2], password):
            flash("Invalid username or password")
            return render_template("login.html")
        
        # Remember user
        session["user_id"] = rows[0][0]
        session["cash"] = rows[0][3]
        conn.close()

        return redirect("/")
    
    # If request is GET, render the login template
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log out user"""

    session.clear()
    return redirect("/")


@app.route("/add", methods=["GET", "POST"])
def add():
    """Add new book"""

    # If request is POST, get valid title, author and price, and add the book to the book table
    if request.method == "POST":

        # Check if admin provided a title
        title = request.form.get("title")
        if not title:
            flash("Please provide a title")
            return render_template("add.html")
        
        # Check if admin provided an author
        author = request.form.get("author")
        if not author:
            flash("Please provide an author")
            return render_template("add.html")
        
        # Check if admin provided a valid price
        try:
            price = float(request.form.get("price"))
        except ValueError:
            flash("Please provide a price")
            return render_template("add.html")

        # Add the book to the database
        conn = sqlite3.connect("library.db")
        db = conn.cursor()
        db.execute("INSERT INTO books (title, author, price) VALUES (?, ?, ?)", (title, author, price))
        conn.commit()
        conn.close()

        return redirect("/")
    
    # If request is GET, render the add template
    else:
        return render_template("add.html")
    

@app.route("/remove", methods=["GET", "POST"])
def remove():
    """Remove a book"""

    # If request is POST, get valid title and author, and remove the book from the books table
    if request.method == "POST":

        # Check if admin provided a title
        title = request.form.get("title")
        if not title:
            flash("Please provide a title")
            return render_template("remove.html")
        
        # Check if admin provided an author
        author = request.form.get("author")
        if not author:
            flash("Please provide an author")
            return render_template("remove.html")
        
        conn = sqlite3.connect("library.db")
        db = conn.cursor()
        db.execute("SELECT * FROM books WHERE title = ? AND author = ? AND user_id = 1 LIMIT 1", (title, author))
        book = db.fetchall()

        # Check if book exists
        if not book:
            flash("Book not found")
            return render_template("remove.html")
        book_id = book[0][0]

        # Remove book from database
        db.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()
        conn.close()

        return redirect("/")
    
    # If request is GET, render the remove template
    else:
        return render_template("remove.html")


@app.route("/history")
def history():
    """History of purchases"""

    conn = sqlite3.connect("library.db")
    db = conn.cursor()
    db.execute("SELECT * FROM history")
    history = db.fetchall()
    conn.close()
    return render_template("history.html", history=history)


@app.route("/portfolio")
def portfolio():
    """Customer's personal portfolio"""

    user = session["user_id"]
    cash = session["cash"]

    conn = sqlite3.connect("library.db")
    db = conn.cursor()
    db.execute("SELECT title, author, price FROM books WHERE user_id = ? GROUP BY title", (user,))
    books = db.fetchall()
    return render_template("portfolio.html", books=books, cash=cash)


@app.route("/buy_book", methods = ["POST"])
def buy_book():
    """Purchase verification"""

    user = session["user_id"]
    cash = session["cash"]
    
    # If customer clicks the "no" button, the purchase is canceled 
    answer = request.form.get("answer")
    if answer == "No":
        return redirect("/")
    
    # If customer clicks the "yes" button, the book is added to the customer's portfolio and the book's user_id becomes the same as the customer's id
    else:
        book_id = request.form.get("id")

        conn = sqlite3.connect("library.db")
        db = conn.cursor()

        db.execute("SELECT title, author, price FROM books WHERE id =?", (book_id,) )
        book = db.fetchall()[0]
        title = book[0]
        author = book[1]
        price = book[2]

        # Check if customer has enough cash in their account
        if cash < price :
            flash("Not enough cash")
            return render_template("/")

        # Update customer's balance    
        session["cash"] -= price
        db.execute("UPDATE users SET cash = ? WHERE id = ?", (session["cash"], user))

        db.execute("UPDATE books SET user_id = ? WHERE id = ?", (user, book_id))
        db.execute("INSERT INTO history (user_id, title, author) VALUES (?, ?, ?)", (user, title, author))
        conn.commit()
        conn.close()
        return redirect("/portfolio")


@app.route("/add_cash", methods=["GET", "POST"])
def add_cash():
    """Add cash to customer's account"""

    # If request is POST, get a valid amount of cash and add it to the customers's account
    if request.method == "POST":
        user = session["user_id"]
        conn = sqlite3.connect("library.db")
        db = conn.cursor()

        # Check if customer provided a valid cash amount
        try:
            add_cash = float(request.form.get("add_cash"))
        except ValueError:
            flash("Please provide a valid amount")
            return render_template("add_cash.html")

        if add_cash < 0:
            flash("Please provide a valid amount")
            return render_template("add_cash.html")
        
        # Add the amount to customer's account
        session["cash"] += add_cash
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", (add_cash, user))

        conn.commit()
        conn.close()
        return redirect("/")

    # If request is GET, render the add_cash template
    else:
        return render_template("add_cash.html")
    

@app.route("/edit", methods = ["POST"])
def edit():
    """Increase or decrease book count"""

    conn = sqlite3.connect("library.db")
    db = conn.cursor()

    # Get admin's input and book's id
    edit = request.form.get("edit")
    id = request.form.get("id")

    # Get the details of the book using the book id
    db.execute("SELECT title, author, price FROM books WHERE id = ?", (id,))
    book = db.fetchall()[0]
    title = book[0]
    author = book[1]
    price = book[2]

    # If admin pressed the +1 button, create an duplicate of the book with a new id
    if edit == "+1":
        db.execute("INSERT INTO books (title, author, price, user_id) VALUES (?, ?, ?, 1)", (title, author, price))

    # If admin pressed the -1 button, remove book from database
    else:
        db.execute("DELETE FROM books WHERE id = ?", (id,))

    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/search", methods = ["GET", "POST"])
def search():
    """Search for a book"""

    cash = session["cash"]

    # If request is POST, get keyword and type of search, and return all the books that contain the keyword
    if request.method == "POST":
        keyword = "%" + request.form.get("keyword") + "%"
        if not keyword:
            flash("Please provide a keyword")
            return render_template("search.html")
        
        # Get the type of search from the selection tag
        type = request.form.get("search_type")
        
        conn = sqlite3.connect("library.db")
        db = conn.cursor()

        # If type is title, return the books that have keyword in their title
        if type == "title":
            db.execute("SELECT id, title, author, COUNT(title), price FROM books WHERE title LIKE ? AND user_id = 1 GROUP BY title ORDER BY title", (keyword,))

        # If type is author, return the books that have keyword in their author
        else:
            db.execute("SELECT id, title, author, COUNT(title), price FROM books WHERE author LIKE ? AND user_id = 1 GROUP BY author ORDER BY author", (keyword,))
        
        books = db.fetchall()
        print(books)
        conn.close()
        return render_template("index.html", books=books, cash=cash)
    
    # If request is GET, render the search template
    else:
        return render_template("search.html", cash=cash)


app.run(debug=True)
