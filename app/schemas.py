from pydantic import BaseModel
from datetime import datetime


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class Post(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    created_at: datetime

    '''
    Why we need to add Config class? 

    Why is this happening?
    1) Your response model (Post) expects a dictionary, but your FastAPI route is returning a SQLAlchemy object (models.Post).
    2) SQLAlchemy models are not automatically serializable into JSON because they contain metadata, relationships, and special methods that Pydantic doesnt understand.
    3) FastAPI is trying to match your SQLAlchemy model (models.Post) with the Pydantic model (schemas.Post), but it fails because SQLAlchemy objects are not dict-like.
    '''

    class Config:
        from_attributes = True