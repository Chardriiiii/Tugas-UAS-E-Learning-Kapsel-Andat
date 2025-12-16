# File: modules/performance_analysis/routes.py

import matplotlib
matplotlib.use('Agg') # Mode tanpa layar
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
from fastapi import APIRouter, Response, HTTPException
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

# Ganti 'app = FastAPI()' menjadi 'router = APIRouter()'
router = APIRouter()

# --- KONFIGURASI DATABASE KHUSUS ANALISIS ---
# Kita gunakan koneksi sendiri agar aman dan tidak ganggu DB utama E-Learning
DB_USER = "root"
DB_PASSWORD = "akucldaripalembang" # <--- SESUAIKAN PASSWORD (kosongkan jika default)
DB_HOST = "localhost"
DB_NAME = "student_performance_db" # Database hasil import CSV tadi

# Setup Engine
try:
    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")
except Exception as e:
    print(f"Error Koneksi DB Analisis: {e}")

# --- FUNGSI BANTUAN ---
def latih_model_prediksi():
    """Melatih otak AI Regresi secara real-time"""
    df = pd.read_sql("SELECT study_hours_per_week, total_score FROM students", engine)
    X = df[['study_hours_per_week']]
    y = df['total_score']
    model = LinearRegression()
    model.fit(X, y)
    return model

# --- ENDPOINTS (Semua pakai @router, bukan @app) ---

@router.get("/summary", summary="Ringkasan Data CSV")
def get_dashboard_summary():
    """Mendapatkan ringkasan statistik dari dataset CSV."""
    try:
        df = pd.read_sql("SELECT COUNT(*) as total, AVG(total_score) as avg FROM students", engine)
        return {
            "Total Mahasiswa": int(df['total'][0]),
            "Rata-rata Nilai": round(float(df['avg'][0]), 2),
            "Status": "Module AI Ready"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai/prediksi-nilai", summary="AI Prediksi Nilai")
def predict_score(jam_belajar: float = 5):
    """
    🤖 AI Prediksi Nilai (Linear Regression).
    """
    try:
        model = latih_model_prediksi()
        prediksi = model.predict([[jam_belajar]])[0]
        nilai_prediksi = max(0, min(100, round(float(prediksi), 2)))
        
        pesan = ""
        if nilai_prediksi >= 85: pesan = "Wah! Kemungkinan besar dapat A!"
        elif nilai_prediksi >= 70: pesan = "Aman, kemungkinan lulus."
        else: pesan = "Hati-hati, risiko remedial tinggi."

        return {
            "input_jam_belajar": f"{jam_belajar} jam/minggu",
            "prediksi_nilai_akhir": nilai_prediksi,
            "analisis_ai": pesan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai/clustering", summary="AI Clustering Plot")
def get_clustering_plot():
    """🧠 AI Pengelompokan Mahasiswa (K-Means Clustering) - Gambar."""
    try:
        df = pd.read_sql("SELECT study_hours_per_week, total_score FROM students", engine)
        X = df[['study_hours_per_week', 'total_score']]
        
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        df['Cluster'] = kmeans.fit_predict(X)
        
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x='study_hours_per_week', y='total_score', hue='Cluster', data=df, palette='viridis', s=60, alpha=0.8)
        
        centers = kmeans.cluster_centers_
        plt.scatter(centers[:, 0], centers[:, 1], c='red', s=200, marker='X', label='Centroid')
        plt.title('AI Clustering: Tipe Karakter Mahasiswa')
        plt.legend()
        
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plt.close()
        
        return Response(content=img.getvalue(), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/visualisasi/regresi", summary="Grafik Regresi Linear")
def get_regression_plot():
    """Grafik Regresi Linear (Bukti Matematika AI)."""
    try:
        df = pd.read_sql("SELECT study_hours_per_week, total_score FROM students", engine)
        plt.figure(figsize=(10, 6))
        sns.regplot(x='study_hours_per_week', y='total_score', data=df, line_kws={"color": "red"})
        plt.title('Regresi Linear: Belajar vs Nilai')
        
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()
        return Response(content=img.getvalue(), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))