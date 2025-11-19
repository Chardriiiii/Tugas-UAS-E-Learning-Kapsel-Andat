from fastapi import APIRouter, HTTPException
from modules.students.schema.schemas import StudentCreate, StudentResponse
from modules.database import students_db

router = APIRouter()

@router.post("/", response_model=StudentResponse)
def create_student(student: StudentCreate):
    # 1. LOGIKA VALIDASI: Cek apakah NIM atau Email sudah ada
    for s in students_db:
        if s["nim"] == student.nim:
            raise HTTPException(status_code=400, detail="NIM sudah terdaftar!")
        if s["email"] == student.email:
            raise HTTPException(status_code=400, detail="Email sudah terdaftar!")

    # 2. MEMBUAT ID BARU
    # Kita gunakan len(db) + 1 sebagai generator ID sederhana
    new_id = len(students_db) + 1
    
    # 3. MENYIAPKAN DATA MAHASISWA
    new_student = student.dict()
    new_student["id"] = new_id      # Primary Key
    new_student["role"] = "student" # Default role
    
    # 4. SIMPAN KE DATABASE
    students_db.append(new_student)
    
    return new_student