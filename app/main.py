from fastapi import FastAPI, HTTPException, Form, Query, Request, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from auth.authentication import create_access_token, verify_password
from pydantic import BaseModel
from jinja2 import Template
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.models import UserCreate, User, BlogCreate, Blog
from app.dependencies import get_db, get_current_user, oauth2_scheme

app = FastAPI()

# Define your database URL
DATABASE_URL = "sqlite:///./blogdb.db"

# Create a SQLAlchemy engine to connect to the database
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the Base for declarative models
Base = declarative_base()

# Define the Blog model
class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    body = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model for user registration
class UserRegistration(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str

# User Registration
@app.post("/register/")
def register_user(user_create: UserRegistration, db: Session = Depends(get_db)):
    # Check if the user with the given email already exists
    existing_user = db.query(User).filter(User.email == user_create.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")

    db_user = User(**user_create.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# User Login
@app.post("/login/")
def login_user(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if a user with the given email exists
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Validate the password (You should use a password hashing library for this)
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    
    # Implement your authentication logic here (e.g., generate and return a JWT token)
    # After password validation
    token = create_access_token(data={"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}

# Display a list of blogs on the homepage
@app.get("/", response_class=HTMLResponse)
def display_homepage(request: Request, db: Session = Depends(get_db)):
    blogs = db.query(Blog).all()
    return templates.TemplateResponse("homepage.html", {"request": request, "blogs": blogs})

# Create Blog (only accessible to authenticated users)
@app.post("/blogs/create/")
def create_blog(blog_create: BlogCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    blog = Blog(**blog_create.dict(), user_id=current_user.id)
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog  # Removed the response_model parameter

# Edit Blog (only accessible to the author of the blog or admin)
@app.put("/blogs/{blog_id}/edit/")
def edit_blog(
    blog_id: int,
    title: str = Form(...),
    body: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    
    if blog.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    # Update the title and body of the blog
    blog.title = title
    blog.body = body

    db.commit()
    db.refresh(blog)
    return blog

# Article creation page
@app.get("/create_article/", response_class=HTMLResponse)
def create_article_page(request: Request, current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You must be logged in to create an article")
    return templates.TemplateResponse("create_article.html", {"request": request, "current_user": current_user})

# Handle the form submission to create a new article
@app.post("/create_article/")
async def create_article(
    request: Request,
    title: str = Form(...),
    body: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You must be logged in to create an article")
    
    # Create the new article
    new_article = Blog(title=title, body=body, user_id=current_user.id)
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    
    # Return a response, redirect, or render a confirmation page as needed
    return {"message": "Article created successfully"}