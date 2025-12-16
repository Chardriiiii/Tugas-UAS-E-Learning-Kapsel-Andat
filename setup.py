import pandas as pd
from sqlalchemy import create_engine, text  # <--- Perhatikan ada import 'text'
import os

# --- KONFIGURASI (GANTI PASSWORD DISINI) ---
DB_USER = "root"
# Jika tadi error password, kemungkinan password Anda kosong.
# Coba kosongkan dulu (""). Jika gagal, baru ganti "root".
DB_PASSWORD = "akucldaripalembang"  # <--- SESUAIKAN
DB_HOST = "localhost"
DB_NAME = "student_performance_db"

def main():
    print("🚀 MEMULAI SETUP DATABASE OTOMATIS...")
    
    # 1. Buat Koneksi Awal (Tanpa nama DB)
    # Ini untuk login ke MySQL secara umum dulu
    engine_root = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}")
    
    try:
        with engine_root.connect() as conn:
            # --- PERBAIKAN DISINI ---
            # Kita bungkus perintah SQL dengan text()
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
            
        print(f"✅ Database '{DB_NAME}' siap/terdeteksi.")
    except Exception as e:
        print(f"❌ Gagal koneksi awal: {e}")
        print("Saran: Cek apakah DB_PASSWORD di file ini sudah benar?")
        return

    # 2. Koneksi ke Database Spesifik (student_performance_db)
    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

    # 3. Baca CSV
    csv_file = 'Students Performance Dataset.csv'
    if not os.path.exists(csv_file):
        print("❌ ERROR: File CSV tidak ditemukan! Pastikan file ada di folder yang sama.")
        return

    print("📖 Membaca file CSV...")
    try:
        df = pd.read_csv(csv_file)
        
        # Bersihkan nama kolom (hapus spasi, ubah ke huruf kecil)
        df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.lower()
        
        # 4. Masukkan ke MySQL
        print("💾 Mengirim data ke MySQL...")
        df.to_sql('students', con=engine, if_exists='replace', index=False)
        
        print(f"🎉 SUKSES BESAR! {len(df)} data berhasil masuk ke tabel 'students'.")
        print("👉 Sekarang jalankan: python analisis.py")
        
    except Exception as e:
        print(f"❌ Error saat proses data: {e}")

if __name__ == "__main__":
    main()