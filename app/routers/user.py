from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from app.database import  get_db
from app import models, schemas, utils
import psycopg2
from psycopg2.extras import RealDictCursor

router = APIRouter(
    prefix="/users",
    tags=['users']
)

# Connecting python to Postgresql database using psycopg2 library. 
try:
    conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='Linkinpark@123', cursor_factory=RealDictCursor)
    """ Normally, when you fetch data using a cursor in psycopg2, you get a tuple, like this: ('Post Title', 'Some content', True)
    But when you use RealDictCursor, you get a dictionary, like this:
    {
    'title': 'Post Title',
    'content': 'Some content',
    'published': True
    }
    This means each row is returned as a Python dictionary where the keys are column names — super useful for APIs and JSON responses.

       """
    cursor = conn.cursor()
    print("Database connection was successful")
except Exception as error:
    print("Connecting to database failed")
    print("Error ", error)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    # Hasing the password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.get('/{id}', response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
    return user