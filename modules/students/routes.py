from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, func 
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from database import get_db, Base, engine

# Import Model Course dan Prerequisite
from modules.courses.routes import CourseModel, PrerequisiteModel

router = APIRouter()

# ==============================
# 1. MODEL DATABASE
# ==============================

class StudentModel(Base):
    __tablename__ = "student_scores"
    student_id = Column(String(50), primary_key=True, index=True) 
    full_name = Column(String(100))
    gender = Column(String(20))
    age = Column(Integer)
    department = Column(String(100))
    attendance_ = Column(Float)
    total_score = Column(Float)
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
    final_score = Column(Float, nullable=True) 
    grade = Column(String(50), nullable=True)

Base.metadata.create_all(bind=engine)

# ==============================
# 2. SCHEMAS
# ==============================

class EnrollRequest(BaseModel):
    course_id: int

class EnrollResponse(BaseModel):
    enrollment_id: int = Field(serialization_alias="enrollment_id")
    student_id: str
    course_id: int
    progress: float
    is_completed: bool
    grade: Optional[str] = None
    final_score: Optional[float] = None

    @field_validator('grade', mode='before')
    def set_course_status_message(cls, v, info):
        if v is None:
            return "Course in Progress (Not Completed)"
        return v

    class Config:
        from_attributes = True

class StudentBase(BaseModel):
    full_name: str
    gender: str
    age: int
    department: str

class StudentCreate(StudentBase):
    student_id: str

class StudentResponse(StudentBase):
    student_id: str
    grade: Optional[str] = None
    enrollments: List[EnrollResponse] = [] 

    @field_validator('grade', mode='before')
    def set_grade_message(cls, v):
        if v is None:
            return "In Progress (Semester Baru)"
        return v

    class Config:
        from_attributes = True

# ==============================
# 3. ROUTES
# ==============================

@router.get("/", response_model=List[StudentResponse])
def read_students(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    students = db.query(StudentModel).offset(skip).limit(limit).all()
    results = []
    for s in students:
        s_dict = StudentResponse.model_validate(s)
        s_dict.enrollments = db.query(EnrollmentModel).filter(EnrollmentModel.student_id == s.student_id).all()
        results.append(s_dict)
    return results

@router.get("/{student_id}", response_model=StudentResponse)
def read_student(student_id: str, db: Session = Depends(get_db)):
    student = db.query(StudentModel).filter(StudentModel.student_id == student_id).first()
    if not student: 
        raise HTTPException(status_code=404, detail="Student not found")
    
    my_enrollments = db.query(EnrollmentModel).filter(EnrollmentModel.student_id == student_id).all()
    response = StudentResponse.model_validate(student)
    response.enrollments = my_enrollments
    return response

# --- UPDATE PENTING DI SINI (LOGIKA PRASYARAT) ---
@router.post("/{student_id}/enroll", response_model=EnrollResponse)
def enroll_course(student_id: str, request: EnrollRequest, db: Session = Depends(get_db)):
    # 1. Cek Mahasiswa
    student = db.query(StudentModel).filter(StudentModel.student_id == student_id).first()
    if not student: raise HTTPException(status_code=404, detail="Mahasiswa tidak ditemukan")
    
    # 2. Cek Matkul
    course = db.query(CourseModel).filter(CourseModel.id == request.course_id).first()
    if not course: raise HTTPException(status_code=404, detail="Mata kuliah tidak ditemukan")

    # =========================================================
    # 🆕 LOGIKA BARU: CEK PRASYARAT (PREREQUISITE CHECK)
    # =========================================================
    
    # Cek apakah mata kuliah ini punya syarat?
    prereq_rule = db.query(PrerequisiteModel).filter(PrerequisiteModel.course_id == request.course_id).first()
    
    if prereq_rule:
        required_course_id = prereq_rule.prereq_id
        
        # Cek apakah mahasiswa SUDAH LULUS mata kuliah syarat tersebut
        # Syarat Lulus: Ada di enrollment history DAN is_completed = True
        has_passed = db.query(EnrollmentModel).filter(
            EnrollmentModel.student_id == student_id,
            EnrollmentModel.course_id == required_course_id,
            EnrollmentModel.is_completed == True 
        ).first()

        if not has_passed:
            # Ambil nama matkul syarat untuk pesan error yang jelas
            prereq_name = db.query(CourseModel).filter(CourseModel.id == required_course_id).first().course_name
            raise HTTPException(
                status_code=400, 
                detail=f"⛔ Gagal Enroll: Anda belum lulus mata kuliah prasyarat: {prereq_name}"
            )
    # =========================================================

    # 3. Cek Duplikasi
    existing = db.query(EnrollmentModel).filter(
        EnrollmentModel.student_id == student_id, EnrollmentModel.course_id == request.course_id
    ).first()
    if existing: raise HTTPException(status_code=400, detail="Sudah terdaftar di mata kuliah ini.")

    # 4. Validasi SKS (Max 24)
    current_credits = db.query(func.sum(CourseModel.credits))\
        .join(EnrollmentModel, CourseModel.id == EnrollmentModel.course_id)\
        .filter(
            EnrollmentModel.student_id == student_id,
            EnrollmentModel.semester == "Ganjil 2025" 
        ).scalar() or 0
    
    projected_credits = current_credits + course.credits

    if projected_credits > 24:
        raise HTTPException(
            status_code=400, 
            detail=f"Gagal Enroll: Batas SKS terlampaui (Max 24). Total Anda: {current_credits}, Ditambah: {course.credits} = {projected_credits}."
        )

    # 5. Simpan Enrollment
    new_enroll = EnrollmentModel(
        student_id=student_id, 
        course_id=request.course_id, 
        progress=0.0,
        grade=None 
    )
    db.add(new_enroll)
    db.commit()
    db.refresh(new_enroll)
    return new_enroll

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