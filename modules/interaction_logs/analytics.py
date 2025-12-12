from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
from database import get_db

router = APIRouter()

def get_df(db):
    query = text("SELECT * FROM student_scores")
    return pd.read_sql(query, db.bind)

@router.get("/study-duration")
def avg_study_duration(db: Session = Depends(get_db)):
    df = get_df(db)
    if df.empty: return {"msg": "No Data"}
    avg = df['study_hours_per_week'].mean()
    by_dept = df.groupby('department')['study_hours_per_week'].mean().to_dict()
    return {"overall_avg_hours": round(avg, 2), "by_department": by_dept}

@router.get("/participation")
def participation_levels(db: Session = Depends(get_db)):
    df = get_df(db)
    if df.empty: return {"msg": "No Data"}
    high = len(df[df['participation_score'] > 80])
    low = len(df[df['participation_score'] < 50])
    return {"high_participation_count": high, "low_participation_count": low}

@router.get("/correlation")
def activity_grade_correlation(db: Session = Depends(get_db)):
    df = get_df(db)
    if df.empty: return {"msg": "No Data"}
    corr = df['study_hours_per_week'].corr(df['total_score'])
    return {"correlation_study_vs_grade": round(corr, 4)}

@router.get("/at-risk")
def identify_at_risk(db: Session = Depends(get_db)):
    df = get_df(db)
    if df.empty: return {"msg": "No Data"}
    # Menggunakan nama kolom yang benar dari import_data.py
    # Biasanya 'attendance_' (lowercase, underscore)
    col_attend = 'attendance_' if 'attendance_' in df.columns else 'attendance'
    
    risk_df = df[df[col_attend] < 70]
    return {
        "count": len(risk_df),
        "students": risk_df[['student_id', 'full_name', col_attend]].to_dict(orient='records')
    }