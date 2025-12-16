import matplotlib
matplotlib.use('Agg') # Mode backend non-GUI agar tidak error di server
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import numpy as np
import os # <--- Import OS
from dotenv import load_dotenv # <--- Import DotEnv

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
# SEKARANG DINAMIS: Mengambil dari .env
# Tidak ada lagi password yang hardcoded di sini.

load_dotenv() # Load file .env

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Validasi sederhana (opsional)
if not all([DB_HOST, DB_USER, DB_NAME]):
    print("⚠️ Warning: Variabel environment database belum lengkap di analytics.py")

# String koneksi khusus untuk fitur AI (menggunakan Pandas read_sql)
CSV_DB_CONN = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

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
    try:
        # Mengambil dari tabel interaction_logs yang sudah kita buat
        query = text("SELECT * FROM interaction_logs")
        return pd.read_sql(query, db.bind)
    except:
        return pd.DataFrame() 

def latih_model_prediksi():
    """Melatih otak AI Regresi menggunakan data dari DB CSV"""
    # Mengambil data dari tabel student_scores (profil siswa & nilai)
    try:
        df = pd.read_sql("SELECT study_hours_per_week, total_score FROM student_scores", engine_csv)
        if df.empty: return None
        
        X = df[['study_hours_per_week']]
        y = df['total_score']
        model = LinearRegression()
        model.fit(X, y)
        return model
    except Exception as e:
        print(f"Error training model: {e}")
        return None

# ==========================================
# 3. ENDPOINT ANALISIS LOGS (FITUR LAMA)
# ==========================================

@router.get("/study-duration", summary="Rata-rata Durasi Belajar (Logs)")
def avg_study_duration(db: Session = Depends(get_db)):
    """Menghitung rata-rata durasi belajar dari Log Interaksi."""
    df = get_df_logs(db)
    if df.empty: return {"msg": "No Data in Logs"}
    
    # Hitung rata-rata durasi (detik -> menit)
    avg_seconds = df['duration_seconds'].mean()
    return {
        "overall_avg_seconds": round(avg_seconds, 2),
        "overall_avg_minutes": round(avg_seconds / 60, 2)
    }

@router.get("/completion-rate", summary="Tingkat Penyelesaian")
def completion_rate(db: Session = Depends(get_db)):
    df = get_df_logs(db)
    if df.empty: return {"msg": "No Data in Logs"}
    
    completed = len(df[df['status'] == 'completed'])
    total = len(df)
    rate = (completed / total) * 100 if total > 0 else 0
    
    return {"completion_rate": f"{round(rate, 1)}%", "total_activities": total}

# ==========================================
# 4. ENDPOINT AI & VISUALISASI (FITUR BARU)
# ==========================================

@router.get("/csv/summary", summary="Ringkasan Data Nilai (CSV)")
def get_csv_summary():
    """Mengambil ringkasan dari Tabel Nilai Siswa."""
    try:
        df = pd.read_sql("SELECT COUNT(*) as total, AVG(total_score) as avg FROM student_scores", engine_csv)
        return {
            "Total Data Siswa": int(df['total'][0]),
            "Rata-rata Nilai": round(float(df['avg'][0]), 2),
            "Sumber Data": f"MySQL - {DB_NAME}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

@router.get("/csv/ai/prediksi", summary="AI Prediksi Nilai")
def predict_score(jam_belajar: float = 5):
    """🤖 Prediksi nilai berdasarkan jam belajar (Linear Regression)."""
    try:
        model = latih_model_prediksi()
        if not model:
            return {"msg": "Data tidak cukup untuk melatih model AI."}
            
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
        df = pd.read_sql("SELECT study_hours_per_week, total_score FROM student_scores", engine_csv)
        if df.empty: raise HTTPException(status_code=404, detail="Data kosong")

        X = df[['study_hours_per_week', 'total_score']].dropna()
        
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        df['Cluster'] = kmeans.fit_predict(X)
        
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x='study_hours_per_week', y='total_score', hue='Cluster', data=df, palette='viridis', s=60, alpha=0.8)
        plt.title('Clustering Siswa: Rajin vs Pintar')
        plt.xlabel('Jam Belajar per Minggu')
        plt.ylabel('Nilai Total')
        
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
        df = pd.read_sql("SELECT study_hours_per_week, total_score FROM student_scores", engine_csv)
        
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