from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationship with Blog model
    blogs = relationship('Blog', back_populates='user')

class UserCreate(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str

class UserUpdate(BaseModel):
    email: str
    first_name: str
    last_name: str

# Use a password hashing library like passlib to hash and verify passwords
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return password_context.hash(password)

class Blog(Base):
    __tablename__ = 'blogs'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    body = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship with User model
    user = relationship('User', back_populates='blogs')

class BlogCreate(BaseModel):
    title: str
    body: str

class BlogUpdate(BaseModel):
    title: str
    body: str
