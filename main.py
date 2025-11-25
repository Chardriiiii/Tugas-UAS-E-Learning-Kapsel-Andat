from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import StudentPerformance
from typing import List

# Definisi Pydantic Schema (Opsional, tapi penting untuk FastAPI)
from pydantic import BaseModel

class StudentBase(BaseModel):
    # Struktur data yang sama dengan Model Anda
    Student_ID: str
    First_Name: str
    Last_Name: str
    Email: str
    Gender: str
    Age: int
    Department: str
    # Perhatikan nama field di Pydantic harus sesuai dengan atribut Python (tanpa karakter khusus)
    Attendance_Percentage: float
    Midterm_Score: float
    Final_Score: float
    # ... (lanjutkan semua field lainnya)
    
    class Config:
        orm_mode = True # Penting agar Pydantic bisa membaca data dari objek ORM SQLAlchemy


app = FastAPI()

# --- ENDPOINTS API ---

@app.get("/")
def home():
    return {"message": "Server FastAPI berjalan"}

@app.get("/students/", response_model=List[StudentBase])
def get_all_students(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Mengambil daftar siswa dari database.
    """
    students = db.query(StudentPerformance).offset(skip).limit(limit).all()
    if not students:
        raise HTTPException(status_code=404, detail="Tidak ada data siswa ditemukan")
        
    return students

@app.get("/students/{student_id}", response_model=StudentBase)
def get_student_by_id(student_id: str, db: Session = Depends(get_db)):
    """
    Mengambil detail siswa berdasarkan ID.
    """
    student = db.query(StudentPerformance).filter(StudentPerformance.Student_ID == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
    return student