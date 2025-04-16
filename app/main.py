from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional, List
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import app.models as models
import app.schemas as schemas
from app.database import engine, get_db
from sqlalchemy.orm import Session
from app import utils
from app.routers import post, user, auth




models.Base.metadata.create_all(bind=engine)

"""
This line tells SQLAlchemy to create all the database tables that are defined in your models (the ones that inherit from Base), if they don't already exist.

`models.Base`: This is your declarative base — the foundation that all your SQLAlchemy model classes inherit from. (from database.py)

`.metadata`: This stores all the schema information (i.e., table definitions, column types, constraints, etc.) for the models.

`.create_all(bind=engine)`:

It uses the engine (your connection to the DB) to connect.

It goes through all the model classes you've defined.

It checks if the corresponding table exists in the DB.

If not, it creates it.

If it already exists, it does nothing (it won't drop or alter it).

"""

app = FastAPI() # It creates an instance of the FastAPI application.






'''
A cursor is a database object that allows us to interact with the database by executing SQL queries and retrieving results. Think of a cursor as a "pointer" that helps fetch rows from the database step by step.

How does it work?
When you execute a SQL query using the cursor, it sends the query to the PostgreSQL database.
The database processes the query and returns the results to the cursor.
You can then fetch the results from the cursor into your Python program.

Why Use cursor.fetchall()?
Step 1: cursor.execute("SELECT * FROM posts")
Sends the SQL query SELECT * FROM posts to the database.
PostgreSQL runs the query and retrieves all rows from the posts table.
The results are stored inside the cursor (not yet in a Python variable).

Step 2: cursor.fetchall()
This method retrieves all the rows that the cursor is holding.
It returns them as a list of dictionaries (since we used RealDictCursor).
Each dictionary represents one row in the posts table.

'''


# Hard coded dictionary for my API
my_posts = [{"title": "title of post 1", "content":"content of post 1", "id":1},{"title":"Favorite food", "content":"I like pizza", "id":2}]

# Find post function. 
def find_post(id):
    for post in my_posts:
        if post["id"] == id:
            return post


# Finding index of the post which is different from "id"
""" for i, p in enumerate(my_posts):
enumerate() gives you both:
i: the current index (0, 1, 2, ...)
p: the actual post (a dictionary like {'id': 1, 'title': 'Hello'})
if p['id'] == id:
Checks whether the id field in the current post matches the id passed to the function.
return i
If a match is found, it returns the index (not the post itself).
If no match is found, the function returns None by default.
 """
def find_index_post(id):
    for i, p in enumerate(my_posts): 
        if p['id'] == id:
            return i
        

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

# Home page of localhost
@app.get("/")
async def root():
    return {"message": "Hello World"}



