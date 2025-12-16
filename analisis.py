import matplotlib
matplotlib.use('Agg') # Mode tanpa layar (Anti Error Tcl)
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sqlalchemy import create_engine
import os

# --- KONFIGURASI ---
DB_USER = "root"
DB_PASSWORD = "akucldaripalembang" # <--- SESUAIKAN
DB_HOST = "localhost"
DB_NAME = "student_performance_db"

def main():
    print("🎨 MEMULAI GENERASI GRAFIK ANALISIS...")
    
    # Buat folder static jika belum ada
    if not os.path.exists('static'):
        os.makedirs('static')

    # Koneksi
    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")
    df = pd.read_sql("SELECT * FROM students", engine)

    # GRAFIK 1: Heatmap Korelasi
    print("   Creating: Heatmap...")
    plt.figure(figsize=(10, 8))
    # Ambil hanya kolom angka
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt=".1f")
    plt.title('Peta Korelasi Data Mahasiswa')
    plt.tight_layout()
    plt.savefig('static/heatmap.png')
    plt.close()

    # GRAFIK 2: Distribusi Nilai
    print("   Creating: Distribusi Nilai...")
    plt.figure(figsize=(8, 6))
    sns.histplot(df['total_score'], kde=True, color='green')
    plt.title('Sebaran Nilai Total')
    plt.savefig('static/distribusi.png')
    plt.close()

    print("✅ SELESAI! Gambar tersimpan di folder 'static/'.")
    print("👉 Lanjut ke Langkah 3.")

if __name__ == "__main__":
    main()