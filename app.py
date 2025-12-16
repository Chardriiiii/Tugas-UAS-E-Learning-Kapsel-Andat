import matplotlib
matplotlib.use('Agg') # Mode tanpa layar
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import io
import os # <--- Update
from dotenv import load_dotenv # <--- Update
from flask import Flask, jsonify, send_file, request
from flasgger import Swagger
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

# 1. Load Environment Variables
load_dotenv()

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'API Analisis Data & AI Prediksi',
    'uiversion': 3,
    'description': 'Dashboard dengan fitur Machine Learning (Regresi & Clustering) untuk data mahasiswa.'
}
swagger = Swagger(app)

# --- KONFIGURASI DATABASE DINAMIS ---
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")

# Validasi agar tidak error senyap
if not all([DB_USER, DB_HOST, DB_NAME]):
    raise ValueError("❌ Error di app.py: Pastikan file .env sudah diisi dengan benar.")

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# --- FUNGSI BANTUAN MACHINE LEARNING ---
def latih_model_prediksi():
    """Melatih otak AI Regresi secara real-time"""
    try:
        df = pd.read_sql("SELECT study_hours_per_week, total_score FROM students", engine)
        if df.empty:
            raise Exception("Data kosong, tidak bisa training.")
        X = df[['study_hours_per_week']]
        y = df['total_score']
    
        model = LinearRegression()
        model.fit(X, y)
        return model
    except Exception as e:
        print(f"Error Training: {e}")
        return None

# --- ENDPOINTS ---

# 1. AI PREDIKSI (REGRESI)
@app.route('/ai/prediksi-nilai', methods=['GET'])
def predict_score():
    """
    🤖 AI Prediksi Nilai (Supervised Learning)
    ---
    tags:
      - 1. Fitur AI (Machine Learning)
    parameters:
      - name: jam_belajar
        in: query
        type: number
        required: true
        default: 5
        description: "Jika saya belajar X jam seminggu, kira-kira dapat nilai berapa?"
    responses:
      200:
        description: Hasil prediksi
    """
    try:
        hours = float(request.args.get('jam_belajar', 0))
        model = latih_model_prediksi()
        
        if model is None:
            return jsonify({"error": "Model gagal dilatih (cek koneksi DB atau data kosong)"}), 500
        
        # Prediksi
        prediksi = model.predict([[hours]])[0]
        nilai_prediksi = max(0, min(100, round(float(prediksi), 2)))
        
        pesan = ""
        if nilai_prediksi >= 85: pesan = "Wah! Kemungkinan besar dapat A!"
        elif nilai_prediksi >= 70: pesan = "Aman, kemungkinan lulus."
        else: pesan = "Hati-hati, risiko remedial tinggi."

        return jsonify({
            "Input Jam Belajar": f"{hours} jam/minggu",
            "Prediksi Nilai Akhir": nilai_prediksi,
            "Analisis AI": pesan
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. AI CLUSTERING (FITUR BARU!)
@app.route('/ai/clustering', methods=['GET'])
def get_clustering_plot():
    """
    🧠 AI Pengelompokan Mahasiswa (Unsupervised Learning)
    ---
    tags:
      - 1. Fitur AI (Machine Learning)
    description: AI otomatis membagi mahasiswa ke dalam 3 kelompok (Cluster) berdasarkan pola belajar & nilai.
    responses:
      200:
        description: Gambar Scatter Plot hasil Clustering
        content:
          image/png:
            schema:
              type: string
              format: binary
    """
    try:
        # 1. Ambil Data
        df = pd.read_sql("SELECT study_hours_per_week, total_score, first_name FROM students", engine)
        
        if df.empty: return jsonify({"error": "Data kosong"}), 400
        
        # 2. Siapkan Data untuk AI (Hanya butuh Jam Belajar & Nilai)
        X = df[['study_hours_per_week', 'total_score']]
        
        # 3. Latih Model K-Means (Bagi jadi 3 Kelompok)
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        df['Cluster'] = kmeans.fit_predict(X)
        
        # 4. Visualisasi
        plt.figure(figsize=(10, 6))
        
        # Gambar titik-titik (Scatter Plot) dengan warna beda tiap cluster
        sns.scatterplot(
            x='study_hours_per_week',
            y='total_score',
            hue='Cluster',
            data=df,
            palette='viridis',
            s=50,
            alpha=0.7
        )
        
        # Tandai Pusat Cluster (Centroids) - Titik Merah Besar
        centers = kmeans.cluster_centers_
        plt.scatter(centers[:, 0], centers[:, 1], c='red', s=200, marker='X', label='Pusat Kelompok')
        
        plt.title('AI Clustering: Pengelompokan Karakter Mahasiswa')
        plt.xlabel('Jam Belajar per Minggu')
        plt.ylabel('Nilai Total')
        plt.legend(title='Tipe Mahasiswa')
        
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plt.close()
        return send_file(img, mimetype='image/png')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3. GRAFIK REGRESI (Melihat Bukti AI 1)
@app.route('/visualisasi/regresi', methods=['GET'])
def get_regression_plot():
    """
    Grafik Regresi Linear (Bukti Hubungan Belajar & Nilai)
    ---
    tags:
      - 2. Visualisasi Lanjutan
    responses:
      200:
        description: Scatter plot dengan garis regresi
        content:
          image/png:
            schema:
              type: string
              format: binary
    """
    try:
        df = pd.read_sql("SELECT study_hours_per_week, total_score FROM students", engine)
        
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x='study_hours_per_week', y='total_score', data=df, alpha=0.3, color='gray', label='Data Asli')
        sns.regplot(x='study_hours_per_week', y='total_score', data=df, scatter=False, color='red', label='Garis Prediksi AI')
        
        plt.title('Analisis Regresi: Pengaruh Jam Belajar terhadap Nilai')
        plt.xlabel('Jam Belajar per Minggu')
        plt.ylabel('Nilai Total')
        plt.legend()
        
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()
        return send_file(img, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 4. BOXPLOT (Analisis Kesenjangan)
@app.route('/visualisasi/kesenjangan', methods=['GET'])
def get_boxplot():
    """
    Boxplot: Analisis Kesenjangan Pintar vs Kurang (Per Jurusan)
    ---
    tags:
      - 2. Visualisasi Lanjutan
    responses:
      200:
        description: Grafik Boxplot
        content:
          image/png:
            schema:
              type: string
              format: binary
    """
    try:
        df = pd.read_sql("SELECT department, total_score FROM students", engine)
        
        plt.figure(figsize=(12, 6))
        sns.boxplot(x='department', y='total_score', data=df, palette="Set3")
        plt.title('Sebaran & Kesenjangan Nilai per Jurusan')
        plt.xticks(rotation=45)
        
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plt.close()
        return send_file(img, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 5. DASHBOARD UTAMA
@app.route('/dashboard/summary', methods=['GET'])
def get_summary():
    """
    Ringkasan Statistik Kampus
    ---
    tags:
      - 3. Dashboard Dasar
    responses:
      200:
        description: Data ringkas
    """
    try:
        df = pd.read_sql("SELECT COUNT(*) as total, AVG(total_score) as avg FROM students", engine)
        return jsonify({
            "Total Mahasiswa": int(df['total'][0]),
            "Rata-rata Nilai": round(float(df['avg'][0]), 2),
            "Status": "AI Ready (Clustering & Regression)"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🔥 SERVER AI ULTIMATE BERJALAN! Buka: http://127.0.0.1:5001/apidocs")
    app.run(debug=True, port=5001)