from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from pydantic import BaseModel, Field, field_validator # <-- Tambah field_validator
from typing import List, Optional, Union
from datetime import datetime
from database import get_db, Base, engine

from modules.courses.routes import CourseModel

router = APIRouter()

# --- MODEL DATABASE ---
class StudentModel(Base):
    __tablename__ = "student_scores"
    student_id = Column(String(50), primary_key=True, index=True) 
    full_name = Column(String(100))
    gender = Column(String(20))
    age = Column(Integer)
    department = Column(String(100))
    attendance_ = Column(Float)
    total_score = Column(Float)
    
    # Boleh Null (None) di Database
    grade = Column(String(50), nullable=True) 

class EnrollmentModel(Base):
    __tablename__ = "enrollments"
    enrollment_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), index=True)
    course_id = Column(Integer, index=True)
    semester = Column(String(20), default="Ganjil 2025")
    progress = Column(Float, default=0.0)      
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Kolom Nilai Akhir Mata Kuliah
    final_score = Column(Float, nullable=True) 
    grade = Column(String(50), nullable=True) # A, B, C, atau In Progress

Base.metadata.create_all(bind=engine)

# --- SCHEMAS ---
class StudentBase(BaseModel):
    full_name: str
    gender: str
    age: int
    department: str

class StudentResponse(StudentBase):
    student_id: str
    # Grade bisa string panjang sekarang ("In Progress...")
    grade: Optional[str] = None 
    
    # VALIDATOR: Mengubah tampilan Grade jika None
    @field_validator('grade', mode='before')
    def set_grade_message(cls, v):
        if v is None:
            return "In Progress (Semester Baru)"
        return v

    class Config:
        from_attributes = True

class EnrollRequest(BaseModel):
    course_id: int

class EnrollResponse(BaseModel):
    enrollment_id: int = Field(serialization_alias="enrollment_id")
    student_id: str
    course_id: int
    progress: float
    is_completed: bool
    
    # Tambahan: Grade per mata kuliah
    grade: Optional[str] = None
    final_score: Optional[float] = None

    # VALIDATOR: Logika "Message Tertentu"
    @field_validator('grade', mode='before')
    def set_course_status_message(cls, v, info):
        # Jika grade kosong/None, beri pesan informatif
        if v is None:
            return "Course in Progress (Not Completed)"
        return v

    class Config:
        from_attributes = True

# --- ROUTES ---

@router.get("/", response_model=List[StudentResponse])
def read_students(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(StudentModel).offset(skip).limit(limit).all()

@router.get("/{student_id}", response_model=StudentResponse)
def read_student(student_id: str, db: Session = Depends(get_db)):
    student = db.query(StudentModel).filter(StudentModel.student_id == student_id).first()
    if not student: raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.post("/{student_id}/enroll", response_model=EnrollResponse)
def enroll_course(student_id: str, request: EnrollRequest, db: Session = Depends(get_db)):
    student = db.query(StudentModel).filter(StudentModel.student_id == student_id).first()
    if not student: raise HTTPException(status_code=404, detail="Mahasiswa tidak ditemukan")
    
    course = db.query(CourseModel).filter(CourseModel.id == request.course_id).first()
    if not course: raise HTTPException(status_code=404, detail="Mata kuliah tidak ditemukan")

    existing = db.query(EnrollmentModel).filter(
        EnrollmentModel.student_id == student_id, EnrollmentModel.course_id == request.course_id
    ).first()
    
    if existing: raise HTTPException(status_code=400, detail="Sudah terdaftar.")

    new_enroll = EnrollmentModel(
        student_id=student_id, 
        course_id=request.course_id, 
        progress=0.0,
        grade=None # Grade awal kosong
    )
    db.add(new_enroll)
    db.commit()
    db.refresh(new_enroll)
    return new_enroll

@router.get("/{student_id}/my-learning", response_model=List[EnrollResponse])
def get_my_learning(student_id: str, db: Session = Depends(get_db)):
    return db.query(EnrollmentModel).filter(EnrollmentModel.student_id == student_id).all()

# --- DROP COURSE ---
@router.delete("/enrollments/{enrollment_id}")
def drop_course(enrollment_id: int, db: Session = Depends(get_db)):
    enrollment = db.query(EnrollmentModel).filter(EnrollmentModel.enrollment_id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment ID not found")
    
    try:
        db.delete(enrollment)
        db.commit()
        return {"status": "success", "message": "Course dropped successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))