from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List

# Import database dan model
from database import get_db
# Pastikan import ini sesuai dengan lokasi file models.py Anda
from modules.analytics.models import StudentModel

router = APIRouter()

# ==========================================
# 1. API UTAMA: LIHAT DATA MAHASISWA (FILTER)
# ==========================================
@router.get("/students", tags=["Students Data"])
def get_students(
    # --- Parameter Filter (Boleh dikosongkan) ---
    department: Optional[str] = Query(None, description="Filter berdasarkan Jurusan (contoh: Science)"),
    gender: Optional[str] = Query(None, description="Filter Gender (Male/Female)"),
    grade: Optional[str] = Query(None, description="Filter Grade (A/B/C/D/F)"),
    min_score: Optional[float] = Query(None, description="Tampilkan nilai Total Score di atas angka ini"),
    search_name: Optional[str] = Query(None, description="Cari nama depan atau belakang"),
    
    # --- Pagination (Agar tidak berat) ---
    skip: int = 0,
    limit: int = 100,
    
    # --- Koneksi Database ---
    db: Session = Depends(get_db)
):
    """
    Mengambil data mahasiswa dengan berbagai opsi filter.
    """
    # Mulai query ambil semua data
    query = db.query(StudentModel)

    # Terapkan Filter jika user mengisinya
    if department:
        query = query.filter(StudentModel.department == department)
    
    if gender:
        query = query.filter(StudentModel.gender == gender)
        
    if grade:
        query = query.filter(StudentModel.grade == grade)
        
    if min_score is not None:
        query = query.filter(StudentModel.total_score >= min_score)

    if search_name:
        # Mencari nama yang MIRIP (Partial Match)
        search_fmt = f"%{search_name}%"
        query = query.filter(
            (StudentModel.first_name.like(search_fmt)) | 
            (StudentModel.last_name.like(search_fmt))
        )

    # Hitung total data sebelum dipotong limit (untuk info)
    total_found = query.count()

    # Ambil data sesuai limit (Pagination)
    results = query.offset(skip).limit(limit).all()

    return {
        "status": "success",
        "total_data_found": total_found,
        "showing": len(results),
        "data": results
    }

# ==========================================
# 2. API ANALITIK (UNTUK TUGAS PROJECT 3)
# ==========================================

# A. Rata-rata Jam Belajar per Jurusan
@router.get("/analytics/avg-study-hours", tags=["Analytics"])
def get_avg_study_hours(db: Session = Depends(get_db)):
    """
    Menghitung rata-rata jam belajar per minggu berdasarkan jurusan.
    """
    results = db.query(
        StudentModel.department,
        func.avg(StudentModel.study_hours_week).label("avg_hours")
    ).group_by(StudentModel.department).all()
    
    return {"status": "success", "data": results}

# B. Distribusi Grade (Berapa orang dapat A, B, C...)
@router.get("/analytics/grade-distribution", tags=["Analytics"])
def get_grade_distribution(db: Session = Depends(get_db)):
    """
    Menghitung jumlah mahasiswa untuk setiap Grade.
    """
    results = db.query(
        StudentModel.grade,
        func.count(StudentModel.id).label("student_count")
    ).group_by(StudentModel.grade).order_by(StudentModel.grade).all()
    
    return {"status": "success", "data": results}

# C. Identifikasi Mahasiswa "Rawan" (Absensi Rendah)
@router.get("/analytics/low-attendance", tags=["Analytics"])
def get_low_attendance(
    threshold: float = 60.0, # Default di bawah 60% dianggap rendah
    db: Session = Depends(get_db)
):
    """
    Mencari mahasiswa dengan kehadiran di bawah persentase tertentu.
    """
    results = db.query(
        StudentModel.student_id_csv,
        StudentModel.first_name,
        StudentModel.department,
        StudentModel.attendance_pct,
        StudentModel.grade
    ).filter(StudentModel.attendance_pct < threshold).all()
    
    return {
        "status": "success", 
        "threshold": f"Below {threshold}%",
        "count": len(results),
        "data": results
    }

# D. Korelasi Jam Belajar vs Nilai Total (Untuk Grafik Scatter Plot)
@router.get("/analytics/score-vs-hours", tags=["Analytics"])
def get_score_vs_hours(db: Session = Depends(get_db)):
    """
    Mengambil data mentah Jam Belajar vs Nilai Total untuk melihat korelasi.
    """
    results = db.query(
        StudentModel.study_hours_week,
        StudentModel.total_score
    ).all()
    
    return {"status": "success", "data": results}