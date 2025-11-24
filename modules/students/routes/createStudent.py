from fastapi import APIRouter, HTTPException
from modules.students.schema.schemas import StudentCreate, StudentResponse
from modules.database import students_db

router = APIRouter()

@router.post("/", response_model=StudentResponse)
def create_student(student: StudentCreate):
    # 1. Validasi Duplikasi (NIM & Email)
    for s in students_db:
        if s["nim"] == student.nim:
            raise HTTPException(status_code=400, detail="NIM sudah terdaftar!")
        if s["email"] == student.email:
            raise HTTPException(status_code=400, detail="Email sudah terdaftar!")

    # 2. Logic Pembuatan ID Baru yang Aman
    # (Mencari ID terbesar yang ada, lalu ditambah 1. Ini lebih aman daripada len())
    if not students_db:
        new_id = 1
    else:
        # Ambil semua student_id, cari yang paling besar
        max_id = max(s["student_id"] for s in students_db)
        new_id = max_id + 1
    
    # 3. Siapkan Data Mahasiswa Baru
    new_student = student.dict()
    new_student["student_id"] = new_id   # <--- PENTING: Konsisten pakai student_id
    new_student["role"] = "student"
    
    # 4. Simpan ke Database
    students_db.append(new_student)
    
    return new_student