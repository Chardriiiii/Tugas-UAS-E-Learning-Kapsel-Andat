from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import StudentModel
from modules.students.schema.schemas import ResponseModel

# --- INI BAGIAN PENTING YANG HILANG/ERROR ---
router = APIRouter() 
# -------------------------------------------

# 1. Ambil SEMUA data siswa
@router.get("/students/", response_model=ResponseModel)
def get_students(db: Session = Depends(get_db)):
    students = db.query(StudentModel).all()
    return {
        "success": True,
        "message": "Data siswa berhasil diambil",
        "data": students
    }

# 2. Ambil SATU siswa berdasarkan ID
@router.get("/students/{student_id}", response_model=ResponseModel)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
    
    return {
        "success": True,
        "message": "Detail siswa ditemukan",
        "data": student
    }