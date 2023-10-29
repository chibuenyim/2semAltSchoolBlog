from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Blog, BlogCreate, BlogUpdate, User
from app.dependencies import get_db
from auth.authentication import get_current_user
from typing import List


router = APIRouter()

@router.post("/blogs", response_model=Blog)
def create_blog(blog_create: BlogCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    blog = Blog(**blog_create.dict(), user_id=current_user.id)
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog

@router.get("/blogs", response_model=List[Blog])
def get_blogs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    blogs = db.query(Blog).offset(skip).limit(limit).all()
    return blogs

@router.get("/blogs/{blog_id}", response_model=Blog)
def get_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog

@router.put("/blogs/{blog_id}", response_model=Blog)
def update_blog(blog_id: int, blog_update: BlogUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    if blog.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")

    for field, value in blog_update.dict(exclude_unset=True).items():
        setattr(blog, field, value)

    db.commit()
    db.refresh(blog)
    return blog
