from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float
from pydantic import BaseModel
from typing import List, Optional
from database import get_db, Base, engine

router = APIRouter()

# --- Model Database ---
class StudentModel(Base):
    __tablename__ = "student_scores"
    
    student_id = Column(String(50), primary_key=True, index=True) 
    full_name = Column(String(100))
    gender = Column(String(20))
    age = Column(Integer)
    department = Column(String(100))
    
    # Email dihapus karena tidak ada di import_data.py Anda
    
    attendance_ = Column(Float)
    midterm_score = Column(Float)
    final_score = Column(Float)
    total_score = Column(Float)
    grade = Column(String(5))

# --- Pydantic Schema ---
class StudentBase(BaseModel):
    full_name: str
    gender: str
    age: int
    department: str
    # email dihapus

class StudentCreate(StudentBase):
    student_id: str

class StudentResponse(StudentBase):
    student_id: str
    attendance_: Optional[float] = None
    total_score: Optional[float] = None
    grade: Optional[str] = None
    
    class Config:
        from_attributes = True  # <--- UPDATE DISINI (V2)

# --- Routes ---
@router.get("/", response_model=List[StudentResponse])
def read_students(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(StudentModel).offset(skip).limit(limit).all()

@router.get("/{student_id}", response_model=StudentResponse)
def read_student_by_id(student_id: str, db: Session = Depends(get_db)):
    student = db.query(StudentModel).filter(StudentModel.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.post("/", response_model=StudentResponse)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    # Cek duplikasi
    if db.query(StudentModel).filter(StudentModel.student_id == student.student_id).first():
        raise HTTPException(status_code=400, detail="Student ID already exists")
        
    db_student = StudentModel(
        **student.dict(), 
        attendance_=0, 
        midterm_score=0, 
        final_score=0, 
        total_score=0, 
        grade="N/A"
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@router.delete("/{student_id}")
def delete_student(student_id: str, db: Session = Depends(get_db)):
    student = db.query(StudentModel).filter(StudentModel.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}