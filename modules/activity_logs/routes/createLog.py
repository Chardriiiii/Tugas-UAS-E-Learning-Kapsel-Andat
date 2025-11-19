from fastapi import APIRouter, HTTPException
from modules.activity_logs.schema.schemas import LogCreate, LogResponse
from modules.database import activity_logs_db, students_db

router = APIRouter()

@router.post("/", response_model=LogResponse)
def create_activity_log(log: LogCreate):
    # Opsional: Validasi apakah student_id benar-benar ada di database mahasiswa
    student_exists = any(s for s in students_db if s["student_id"] == log.student_id)
    if not student_exists:
        raise HTTPException(status_code=404, detail="Student ID tidak ditemukan")

    # 1. Buat ID Log Baru
    new_log_id = len(activity_logs_db) + 1
    
    # 2. Siapkan Data
    new_log = log.dict()
    new_log["log_id"] = new_log_id  # <--- DISIMPAN SEBAGAI log_id
    
    # 3. Simpan
    activity_logs_db.append(new_log)
    return new_log