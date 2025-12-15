from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, or_
from pydantic import BaseModel, Field
from typing import List, Optional
from database import get_db, Base, engine

router = APIRouter()

class CourseModel(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String(100), nullable=False)
    department = Column(String(50), nullable=True)
    credits = Column(Integer, default=3)

Base.metadata.create_all(bind=engine)

class CourseBase(BaseModel):
    course_name: str
    department: Optional[str] = None
    credits: int = 3

class CourseResponse(CourseBase):
    id: int = Field(serialization_alias="course_id")
    class Config:
        from_attributes = True

@router.get("/", response_model=List[CourseResponse])
def read_courses(department: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(CourseModel)
    if department:
        query = query.filter(or_(CourseModel.department == department, CourseModel.department == "General"))
    return query.all()

@router.post("/", response_model=CourseResponse)
def create_course(course: CourseBase, db: Session = Depends(get_db), x_role: str = Header(default="student")):
    if x_role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Hanya admin.")
    new_course = CourseModel(**course.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course