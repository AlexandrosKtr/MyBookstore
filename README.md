# MyBookstore
### Video Demo:  <(https://youtu.be/Zk17w4xDcyI)>
### Description:
#### ***Summary***:
*MyBookstore* is a web application for a small local bookstore that can be used, by the admin, to manage the book stock of the bookstore, as well as to buy books, as a customer.

#### ***Details:***
##### **Register/Login**
*MyBookstore* has a Register/Login system that handles the creation of user accounts using unique usernames, and passwords that are converted into hashes for added security. 
If the user enters a username that is already taken, a message will flash prompting the user to try to input another username. 
If the user enters a password that is not at least 10 characters long or if the password and the confirmation of the password don't match, a message will flash, prompting the user for a valid password or for the password and the confirmation to match, respectively.

##### **Admin**
After logging in, if the user is the *admin*, the home page presents the list of books that are currently in the database. Each book has a title, an author, an amount of copies with the same title and a price. For each book the *admin* has the ability to increase or decrease its amount of copies using the buttons at the end of each row. Also the *admin* has the ability to add a new book in the database using the "new book" tab or remove a book using the "remove book" tab. Finally the *admin* has access to a "history" tab that showcases all the books that have been bought by users.

##### **Customer**
If the user is not an *admin*, so a *customer*, the home page presents the same list of books that the *admin* has access to, but with a few differences. *Customers* do not have access to the amount of copies of each book and cannot in any way alter that amount. Instead *customers* have the ability to buy any book using the "buy" button at the end of each row, provided that there is enough money in the account. The cash total of each *customer* is presented at the top right of the screen and clicking on that total brings up a new template to allow the *customer* to add any amount of cash that they need. If the *customer* has enough money to buy the book, they are asked to verify the transaction and if they answer "yes", they are redirected to their personal portfolio. There the *customer* can see all the books that they have already bought. Users can also access their personal portfolio using the "My books" tab.

##### **Search**
Both the *admin* and the *customer* have access to a search function, that allows them to search for a specific book, either by title or by author.

### ***Files:***

#### **Static folder**
Stored in the static folder, are:
1. The **bookstore_icon.ico**, that is the icon on the webpage tab
2. The **bookstore_img.jpeg**, that is the image from which the background is created from
3. The **styles.css**, that handles some of the properties of different HTML tags

#### **Templates folder**
Stored in the templates folder, are all the different templates that render throughout the use of *MyBookstore*:
1. **layout.html**  is the basic blueprint from where all the other templates extend from
2. **register.html**  renders when a new *user* wants to register
3. **login.html**  renders when an already registered *user* wants to login
4. **index.html**  renders the home page
5. **add.html**  renders when an *admin* wants to add a new book
6. **remove.html**  renders when an *admin* wants to remove a book
7. **history.html**  renders when an *admin* wants to see the books that were bought by *users*
8. **search.html**  renders when a *user* wants to search for a specific book
9. **buy_book.html**  renders when a *customer* tries to buy a book
10. **portfolio.html**  renders when the *customer* buys a book
11. **add_cash.html**  renders when a *customer* wants to increase their account balance

#### **library.db**
This file is the SQLite3 database for *MyBookstore*, that contains three tables named users, books and history.

Column names:

##### **Users**
1. id
2. username
3. hash
4. cash

##### **books**
1. id
2. title
3. author
4. price
5. user_id

##### **history**
1. request_id
2. user_id
3. title
4. author
5. date_time

#### **helpers.py**
This file contains three functions that contribute to the function of the main *app.py*. The **create_sqlite_database** and **create_tables functions** are used to create the library.db file and the tables within it, if any of those does not already exist. The **login_required** function is a decorator that creates the requirement for logging in, in order to access the application's functionality.

#### **app.py**
This is the main file of the application that contains the bulk of all the different routes and functions that provide the app's functionality.

##### **Routes and Functions**:

1. **after_request**. Ensures responses are not cached.
2. **index**. Home page. If request is POST, get the details of the selected book and render the buy_book template with these details, else if request is GET, get the list of books in the books table that belong to the *admin*.
3. **register**. Register new user. If request is POST, get valid username and password and register user, else if request is GET, render the register template.
4. **login**. User log in. If request is POST, get valid username and password, else if request is GET, render the login template.
5. **logout**. Logs out the user.
6. **add**. Add a new book. If request is POST, get valid title, author and price, and add the book to the book table, else if request is GET, render the add template.
7. **remove**. Remove a book. If request is POST, get valid title and author, and remove the book from the books table, else if request is GET, render the remove template.
8. **history**. Renders the history of purchases through history.html
9. **portfolio**. Renders the *customer's* personal portfolio through portfolio.html
10. **buy_book**. Renders the purchase verification. If *customer* clicks the "no" button, the purchase is canceled, else if *customer* clicks the "yes" button, the book is added to the *customer's* portfolio and the book's user_id becomes the same as the *customer's* id.
11. **add_cash**. Add cash to *customer's* account. If request is POST, get a valid amount of cash and add it to the *customer's* account, else if request is GET, render the add_cash template.
12. **edit**. Increase or decrease book count. If *admin* pressed the +1 button, create a duplicate of the book with a new id, else if *admin* pressed the -1 button, remove book from database.
13. **search**. Search for a book. If request is POST, get keyword and type of search, and return all the books that contain the keyword, else if request is GET, render the search template.


 










