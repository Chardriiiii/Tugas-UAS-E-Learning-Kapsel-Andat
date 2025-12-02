from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text
from pydantic import BaseModel
from typing import List
from database import get_db, Base, engine

router = APIRouter()

class CourseModel(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String(100), nullable=False)
    department = Column(String(50))
    credits = Column(Integer, default=3)

Base.metadata.create_all(bind=engine)

class CourseBase(BaseModel):
    course_name: str
    department: str
    credits: int = 3

class CourseResponse(CourseBase):
    id: int
    class Config:
        from_attributes = True  # <--- UPDATE DISINI (V2)

@router.post("/", response_model=CourseResponse)
def create_course(course: CourseBase, db: Session = Depends(get_db)):
    new_course = CourseModel(**course.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@router.get("/", response_model=List[CourseResponse])
def read_courses(db: Session = Depends(get_db)):
    return db.query(CourseModel).all()

@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(CourseModel).filter(CourseModel.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()
    return {"message": "Course deleted"}