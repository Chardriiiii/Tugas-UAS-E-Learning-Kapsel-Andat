from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
from database import get_db

router = APIRouter()

def get_df(db):
    # Load data dari tabel student_scores (hasil import CSV)
    query = text("SELECT * FROM student_scores")
    return pd.read_sql(query, db.bind)

@router.get("/study-duration")
def avg_study_duration(db: Session = Depends(get_db)):
    """Rata-rata durasi belajar per minggu."""
    df = get_df(db)
    if df.empty: return {"msg": "No Data"}
    
    avg = df['study_hours_per_week'].mean()
    by_dept = df.groupby('department')['study_hours_per_week'].mean().to_dict()
    return {"overall_avg_hours": round(avg, 2), "by_department": by_dept}

@router.get("/participation")
def participation_levels(db: Session = Depends(get_db)):
    """Tingkat partisipasi mahasiswa."""
    df = get_df(db)
    # Asumsi participation_score mewakili keaktifan forum/diskusi
    high = len(df[df['participation_score'] > 80])
    low = len(df[df['participation_score'] < 50])
    return {"high_participation_count": high, "low_participation_count": low}

@router.get("/correlation")
def activity_grade_correlation(db: Session = Depends(get_db)):
    """Hubungan aktivitas vs nilai."""
    df = get_df(db)
    # Korelasi antara durasi belajar dan nilai total
    corr = df['study_hours_per_week'].corr(df['total_score'])
    return {"correlation_study_vs_grade": round(corr, 4), "note": "Mendekati 1 = Hubungan kuat"}

@router.get("/at-risk")
def identify_at_risk(db: Session = Depends(get_db)):
    """Mahasiswa aktivitas rendah (Kehadiran < 70)."""
    df = get_df(db)
    # Cek nama kolom attendance atau attendance_
    att_col = 'attendance_' if 'attendance_' in df.columns else 'attendance'
    
    risk_df = df[df[att_col] < 70]
    return {
        "count": len(risk_df),
        "students": risk_df[['student_id', 'full_name', att_col]].to_dict(orient='records')
    }