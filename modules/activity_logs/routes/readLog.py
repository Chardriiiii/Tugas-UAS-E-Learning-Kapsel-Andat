from fastapi import APIRouter
from typing import List
from modules.activity_logs.schema.schemas import LogResponse
from modules.database import activity_logs_db, students_db

router = APIRouter()

# --- Endpoint Standar ---
@router.get("/", response_model=List[LogResponse])
def get_all_logs():
    return activity_logs_db

# --- Endpoint ANALISIS DATA ---

# 1. Rata-rata durasi belajar
@router.get("/analytics/average-duration")
def get_average_duration():
    if not activity_logs_db:
        return {"average": 0}
    
    total_duration = sum(log["duration"] for log in activity_logs_db)
    avg = total_duration / len(activity_logs_db)
    return {
        "total_logs": len(activity_logs_db),
        "average_duration_minutes": round(avg, 2)
    }

# 2. Identifikasi mahasiswa aktivitas rendah
@router.get("/analytics/low-activity-students")
def get_low_activity_students(threshold_minutes: int = 30):
    # Hitung total durasi per mahasiswa
    student_durations = {}
    
    # Loop data log
    for log in activity_logs_db:
        sid = log["student_id"]
        student_durations[sid] = student_durations.get(sid, 0) + log["duration"]
    
    # Filter yang di bawah threshold
    low_activity = []
    for sid, total_time in student_durations.items():
        if total_time < threshold_minutes:
            # Ambil nama mahasiswa dari DB (pencocokan menggunakan student_id)
            s_name = next((s["name"] for s in students_db if s["student_id"] == sid), "Unknown")
            
            low_activity.append({
                "student_id": sid,
                "name": s_name,
                "total_duration": total_time,
                "status": "Low Activity"
            })
            
    return low_activity