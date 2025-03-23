from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import app.models as models
from app.database import engine, get_db
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()



# Creating a class for "post" using pydantic model for data validation
'''
pydantic models are scheme models which is used for data validation and never interacts with the database

'''
class Post(BaseModel):
    title: str
    content: str
    published: bool = True


# Connecting python to Postgresql database using psycopg2 library. 
try:
    conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='Linkinpark@123', cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print("Database connection was successful")
except Exception as error:
    print("Connecting to database failed")
    print("Error ", error)

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
def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i
        

# Home page of localhost
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    
    post = db.query(models.Post).all()
    return {"data": post}


# 1) "posts" end point and get method to get post with psycopg2

@app.get("/posts")
async def get_post(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
#    cursor.execute(""" SELECT * FROM posts """)
#    posts = cursor.fetchall()
    return {"data":posts}

# From psycopg2
@app.get("/posts-from-psycopg2")
async def get_post():
    cursor.execute(""" SELECT * FROM posts """)
    posts = cursor.fetchall()
    '''
    cursor.execute("SQL QUERY") sends the query to the database.
    cursor.fetchall() retrieves all results from the cursor and stores them in Python.
    Without fetchall(), the data remains inside the cursor and is not available for use.
    '''
    return {"data":posts}

# From SQLalchemy ORM
@app.get("/posts-from-orm")
async def get_post(Session = Depends(get_db)):
    get_posts_from_orm = Session.query(models.Post).all() 
    # Fews things that should be understood
    '''
    1. Here in above code which is main code "/posts" I created an instance of a "Session" in the "db" object
    2. In the next line "models.Post" here are all the details. 
      a. "Post" is the class name where we are going to query with table name as "posts" and "models" is the file name and that's why we are saying "models.post"
      b. When I call "Session.query(models.Post)" it means ---> SELECT * FROM posts because "Post" class has "posts" table in it. 
      c. When you call "Session.query(models.Post)" you are not executing the query yet. Instead, this returns a query object (also known as a QuerySet in some frameworks). This object represents a database query but does not actually fetch data from the database. Since the query is not executed yet, "get_posts" is not a list of results. It is just an object that represents a SQL query.
      d. Above query will not return anything until we ".all()" meaning if you don't apply ".all()" to the query, it will not return any results. 
      e. When you call ".all()", you execute the query and retrieve all matching records as a list.
      f. Here's what happens under the hood:
          SQLAlchemy sends the SQL query to the database.
          The database executes the query and returns the result.
          SQLAlchemy fetches the rows and converts them into Python objects (instances of models.Post).
          These objects are stored in a Python list.
          That list is assigned to get_posts.
      g. If you remove .all(), your function will look like this: get_posts_from_orm = Session.query(models.Post)
          At this point:
          "get_posts_from_orm" is still a query object, not an actual list of results.
          When FastAPI tries to return posts as a response, it doesn't know how to convert a query object into JSON.
          FastAPI expects a list or an iterable of Pydantic models but receives a SQLAlchemy query instead.

    '''
    return {"data":get_posts_from_orm}



# Creating a post using "post" method and also adding HTTP status.
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    #cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.#title, post.content, post.publish))
    #new_post = cursor.fetchone()
    #conn.commit()

    new_post = models.Post(**post.dict())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}


# From psycopg2
@app.post("/create-posts-from-psycopg2", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data":new_post}    


# From SQLalchemy ORM
@app.post("/create-post-from-orm", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db:Session = Depends(get_db)):
    new_post = models.Post(**post.dict())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    '''
    When you insert a new row into the database using SQLAlchemy ORM, the following sequence of events occurs:
    Step 1: Create a New SQLAlchemy Object
        `new_post = models.Post(**post.dict())`
    This creates an instance of the ORM model, but it's not yet stored in the database.
    The new_post object only exists in Python memory.

    Step 2: Add the Object to the Session
        `db.add(new_post)`
    This tells SQLAlchemy to track new_post as a new database record.
    However, the data is not written to the database yet.

    Step 3: Commit the Transaction
        `db.commit()`
    This executes the INSERT INTO posts ... SQL statement.
    The row is officially added to the database.
    At this point, SQLAlchemy loses track of new_post, meaning that any database-generated values (like id, created_at, etc.) might not be updated in your Python object yet.

    Step 4: Refresh the Object
      `db.refresh(new_post)`
    This runs a SELECT query to fetch the latest state of new_post from the database.
    If the database auto-generates fields (like id, created_at, etc.), these values are now available in your Python object.
    Now new_post is fully synchronized with the database.

    '''
    return {"data": new_post}
    

# Get post through it's ID. 
@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    #cursor.execute("""SELECT * FROM posts WHERE id = %s """,(id,))
    #test_post = cursor.fetchone()
    test_post = db.query(models.Post).filter(models.Post.id == id).first()
    print(test_post)

    if not test_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with {id} not found")     
    return {"post_detail": test_post}


# From psycopg2
@app.get("/get-post-by-id-from-psycopg2/{id}")
def get_post(id: int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s """, (id,))
    '''
    ❌ Why Does "RETURNING *" Cause an Error?
      SELECT already returns data from the database.
      RETURNING is used only for modification queries (INSERT, UPDATE, DELETE) to return the modified row(s).
      In a SELECT statement, RETURNING is not valid, so the database raises a syntax error.
    '''
    test_post = cursor.fetchone()
    if not test_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")
    return {"data":test_post}

@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    #cursor.execute("""SELECT * FROM posts WHERE id = %s """,(id,))
    #test_post = cursor.fetchone()
    test_post = db.query(models.Post).filter(models.Post.id == id).first()
    print(test_post)

    if not test_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with {id} not found")     
    return {"post_detail": test_post}

# From orm
@app.get("/get-post-by-id-from-orm/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    test_post = db.query(models.Post).filter(models.Post.id == id).first()
    if not test_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with {id} does not exists")
    return {"data": test_post}
    


# Delete post using it's ID.
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
   
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (id,))
    # deleted_post = cursor.fetchone()
    
    deleted_post = db.query(models.Post).filter(models.Post.id == id)
    if deleted_post.first() == None:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exists")

    deleted_post.delete(synchronize_session=False)
    db.commit()
    #conn.commit()
    return {'message':"post was successfully deleted"}

# From psycopg2
@app.delete("/delete-post-by-psycopg2/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (id,))
    deleted_post = cursor.fetchone()
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} not found")
    conn.commit()
    return {"details":deleted_post}


# From orm
@app.delete("/delete-post-by-orm/{id}")
def delete_post(id: int, db: Session = Depends(get_db)):
    deleted_post = db.query(models.Post).filter(models.Post.id == id)
    if deleted_post.first() == None:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    
    deleted_post.delete(synchronize_session=False)
    db.commit()
    return {"message": "post was deleted succesfully"}
    

# Update post using its ID. 
@app.put("/posts/{id}")
def update_post(id: int, updated_post: Post, db: Session = Depends(get_db)):
    #cursor.execute("""UPDATE posts SET title = %s, content = %s, published= %s WHERE id = %s RETURNING *""", ##(post.title, post.content, post.publish, (id,)))
    #updated_post = cursor.fetchone()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exists")

    post_query.update(updated_post.dict(), synchronize_session=False)
    # conn.commit()
    db.commit()
    return {'data': post_query.first()}

# from psycopg2
@app.put("/update-post-by-psycopg/{id}")
def update_post(id: int, updated_post: Post):
    cursor.execute("""UPDATE posts SET title= %s, content= %s, published= %s WHERE id = %s RETURNING *""", (updated_post.title, updated_post.content, updated_post.published, (id,)))
    updated_post = cursor.fetchone()
    conn.commit()
    return {"data": updated_post}

@app.put("/posts/{id}")
def update_post(id: int, updated_post: Post, db: Session = Depends(get_db)):
    #cursor.execute("""UPDATE posts SET title = %s, content = %s, published= %s WHERE id = %s RETURNING *""", ##(post.title, post.content, post.publish, (id,)))
    #updated_post = cursor.fetchone()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exists")

    post_query.update(updated_post.dict(), synchronize_session=False)
    # conn.commit()
    db.commit()
    return {'data': post_query.first()}


# from orm
@app.put("/update-post-by-orm/{id}")
def updated_post(id: int, updat_post: Post, db: Session = Depends(get_db)):
    u_post = db.query(models.Post).filter(models.Post.id == id)
    post = u_post.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post not found")
    
    u_post.update(updat_post.dict(), synchronize_session=False)
    db.commit()
    return {"data":u_post.first()}