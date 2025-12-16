import matplotlib
matplotlib.use('Agg') # Mode backend non-GUI agar tidak error di server
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import numpy as np


from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import text, create_engine
from database import get_db
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans


router = APIRouter()


# ==========================================
# 1. KONFIGURASI DATABASE TAMBAHAN (CSV/AI)
# ==========================================
# Ini adalah bagian yang tadinya hilang.
# Kita butuh ini karena data nilai ada di database 'student_performance_db',
# sedangkan log tracking ada di database default project Anda.


DB_USER = "root"
DB_PASSWORD = "akucldaripalembang" # <--- SESUAIKAN PASSWORD (kosongkan jika default)
DB_HOST = "localhost"
DB_NAME_CSV = "student_performance_db"


# String koneksi khusus untuk fitur AI
CSV_DB_CONN = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME_CSV}"


try:
    # Engine khusus untuk membaca data CSV/Nilai
    engine_csv = create_engine(CSV_DB_CONN)
except Exception as e:
    print(f"Warning: Koneksi DB Analisis CSV Gagal: {e}")


# ==========================================
# 2. FUNGSI BANTUAN (HELPER)
# ==========================================


def get_df_logs(db):
    """Mengambil data logs dari database utama project (E-Learning Logs)"""
    # Sesuaikan 'student_scores' dengan nama tabel log Anda yang sebenarnya
    try:
        query = text("SELECT * FROM student_scores")
        return pd.read_sql(query, db.bind)
    except:
        return pd.DataFrame() # Return kosong jika tabel belum ada


def latih_model_prediksi():
    """Melatih otak AI Regresi menggunakan data dari DB CSV"""
    # Menggunakan engine_csv (bukan db session utama)
    df = pd.read_sql("SELECT study_hours_per_week, total_score FROM students", engine_csv)
    X = df[['study_hours_per_week']]
    y = df['total_score']
    model = LinearRegression()
    model.fit(X, y)
    return model


# ==========================================
# 3. ENDPOINT ANALISIS LOGS (FITUR LAMA)
# ==========================================


@router.get("/study-duration", summary="Rata-rata Durasi Belajar (Logs)")
def avg_study_duration(db: Session = Depends(get_db)):
    df = get_df_logs(db)
    if df.empty: return {"msg": "No Data in Logs"}
   
    # Cek ketersediaan kolom sebelum akses
    col_hours = 'study_hours_per_week'
    if col_hours not in df.columns: return {"msg": f"Kolom {col_hours} tidak ditemukan"}


    avg = df[col_hours].mean()
    if 'department' in df.columns:
        by_dept = df.groupby('department')[col_hours].mean().to_dict()
    else:
        by_dept = {"General": avg}
       
    return {"overall_avg_hours": round(avg, 2), "by_department": by_dept}


@router.get("/participation", summary="Tingkat Partisipasi (Logs)")
def participation_levels(db: Session = Depends(get_db)):
    df = get_df_logs(db)
    if df.empty: return {"msg": "No Data in Logs"}
   
    if 'participation_score' not in df.columns: return {"msg": "Kolom participation_score tidak ditemukan"}


    high = len(df[df['participation_score'] > 80])
    low = len(df[df['participation_score'] < 50])
    return {"high_participation_count": high, "low_participation_count": low}


@router.get("/correlation", summary="Korelasi Log vs Nilai (Logs)")
def activity_grade_correlation(db: Session = Depends(get_db)):
    df = get_df_logs(db)
    if df.empty: return {"msg": "No Data in Logs"}
   
    if 'total_score' in df.columns and 'study_hours_per_week' in df.columns:
        corr = df['study_hours_per_week'].corr(df['total_score'])
        return {"correlation_study_vs_grade": round(corr, 4)}
    return {"msg": "Kolom data kurang lengkap untuk korelasi"}


@router.get("/at-risk", summary="Identifikasi Mahasiswa Berisiko (Logs)")
def identify_at_risk(db: Session = Depends(get_db)):
    df = get_df_logs(db)
    if df.empty: return {"msg": "No Data in Logs"}
   
    possible_cols = ['attendance_', 'attendance_pct', 'attendance']
    col_attend = next((col for col in possible_cols if col in df.columns), None)
   
    if col_attend:
        risk_df = df[df[col_attend] < 70]
        # Cari nama kolom nama yang tersedia
        name_col = next((col for col in ['full_name', 'first_name', 'name'] if col in df.columns), 'student_id')
       
        return {
            "count": len(risk_df),
            "students": risk_df[['student_id', name_col, col_attend]].to_dict(orient='records')
        }
    return {"msg": "Kolom attendance tidak ditemukan"}


# ==========================================
# 4. ENDPOINT AI & VISUALISASI (FITUR BARU)
# ==========================================
# Endpoint ini menggunakan engine_csv (Database Student Performance)


@router.get("/csv/summary", summary="Ringkasan Data Nilai (CSV)")
def get_csv_summary():
    """Mengambil ringkasan dari Database Student Performance (CSV)."""
    try:
        df = pd.read_sql("SELECT COUNT(*) as total, AVG(total_score) as avg FROM students", engine_csv)
        return {
            "Total Data Siswa": int(df['total'][0]),
            "Rata-rata Nilai": round(float(df['avg'][0]), 2),
            "Sumber Data": "MySQL - student_performance_db"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")


@router.get("/csv/ai/prediksi", summary="AI Prediksi Nilai")
def predict_score(jam_belajar: float = 5):
    """🤖 Prediksi nilai berdasarkan jam belajar (Linear Regression)."""
    try:
        model = latih_model_prediksi()
        prediksi = model.predict([[jam_belajar]])[0]
        nilai_prediksi = max(0, min(100, round(float(prediksi), 2)))
       
        pesan = "Perlu Bimbingan"
        if nilai_prediksi >= 85: pesan = "Sangat Memuaskan (A)"
        elif nilai_prediksi >= 70: pesan = "Lulus (B/C)"
       
        return {
            "input_jam": jam_belajar,
            "prediksi_nilai": nilai_prediksi,
            "analisis": pesan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/csv/ai/clustering", summary="Visualisasi Clustering (Gambar)")
def get_clustering_plot():
    """🧠 Gambar hasil K-Means Clustering."""
    try:
        df = pd.read_sql("SELECT study_hours_per_week, total_score FROM students", engine_csv)
        X = df[['study_hours_per_week', 'total_score']]
       
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        df['Cluster'] = kmeans.fit_predict(X)
       
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x='study_hours_per_week', y='total_score', hue='Cluster', data=df, palette='viridis', s=60, alpha=0.8)
       
        # Gambar buffer
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plt.close()
        return Response(content=img.getvalue(), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/csv/visualisasi/regresi", summary="Visualisasi Regresi (Gambar)")
def get_regression_plot():
    """📉 Gambar Garis Regresi Linear."""
    try:
        df = pd.read_sql("SELECT study_hours_per_week, total_score FROM students", engine_csv)
       
        plt.figure(figsize=(10, 6))
        sns.regplot(x='study_hours_per_week', y='total_score', data=df, line_kws={"color": "red"})
        plt.title('Regresi: Jam Belajar vs Nilai')
       
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()
        return Response(content=img.getvalue(), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))