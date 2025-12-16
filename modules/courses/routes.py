from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, ForeignKey, or_ # <--- Tambah ForeignKey
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from database import get_db, Base, engine

router = APIRouter()

# ==============================
# 1. MODEL DATABASE
# ==============================

class CourseModel(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String(100), nullable=False)
    department = Column(String(50), nullable=True)
    credits = Column(Integer, default=3)

# --- TAMBAHAN BARU: TABEL PRASYARAT ---
class PrerequisiteModel(Base):
    __tablename__ = "prerequisites"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id")) # Matkul yang mau diambil
    prereq_id = Column(Integer, ForeignKey("courses.id")) # Syaratnya apa

Base.metadata.create_all(bind=engine)

# ==============================
# 2. PYDANTIC SCHEMAS
# ==============================

class CourseBase(BaseModel):
    course_name: str
    department: Optional[str] = None
    credits: int = Field(..., ge=2, le=6)

class CourseResponse(CourseBase):
    id: int = Field(serialization_alias="course_id")

    class Config:
        from_attributes = True

# ==============================
# 3. ROUTES
# ==============================

@router.get("/", response_model=Dict[str, List[CourseResponse]])
def read_courses(department: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(CourseModel)
    
    if department:
        query = query.filter(CourseModel.department == department)
        
    courses = query.all()
    
    grouped_courses = {}
    for course in courses:
        dept_name = course.department.title() if course.department else "General"
        
        if dept_name not in grouped_courses:
            grouped_courses[dept_name] = []
            
        grouped_courses[dept_name].append(course)
        
    return grouped_courses

@router.post("/", response_model=CourseResponse)
def create_course(course: CourseBase, db: Session = Depends(get_db), x_role: str = Header(default="student")):
    if x_role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Hanya admin.")
    
    new_course = CourseModel(**course.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course