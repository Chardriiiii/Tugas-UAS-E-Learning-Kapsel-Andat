import pandas as pd
import mysql.connector
from mysql.connector import Error # Tambahkan ini agar Error dapat tertangkap

# --- 1. KONFIGURASI KONEKSI DATABASE ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "616047SN", 
    "database": "DATAUAS_db"
}

CSV_FILE = "Students Performance Dataset.csv"
TABLE_NAME = "DATAUAS" # PASTIKAN NAMA TABEL INI SUDAH DIGANTI DARI 'student_performance' ke 'DATAUAS'

# --- 2. FUNGSI TRANSFORMASI (Membersihkan Nama Kolom) ---
def clean_column_names(df):
    """
    Menyesuaikan nama kolom DataFrame agar cocok dengan skema tabel MySQL.
    PERHATIAN: Menggunakan '_Percent' di sini, pastikan cocok dengan skema SQL Anda.
    """
    # Mengganti ' (%)' menjadi '_Percent' dan membersihkan yang lain
    df.columns = df.columns.str.replace(' \(%\)', '_Percent', regex=True).str.replace(' \(1-10\)', '', regex=True).str.replace('[^0-9a-zA-Z_]+', '_', regex=True)
    return df

# --- 3. FUNGSI UTAMA PEMUATAN DATA (Seeding) ---
def load_data_to_mysql():
    conn = None # Inisialisasi conn di luar try
    print(f"Mulai memuat data dari {CSV_FILE}...")
    
    try:
        # E: Extract (Membaca file CSV)
        df = pd.read_csv(CSV_FILE)
        
        # T: Transform (Membersihkan nama kolom)
        df = clean_column_names(df)
        
        # Koneksi ke MySQL
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Persiapan Query INSERT
        columns = df.columns.tolist()
        columns_sql = ", ".join([f"`{col}`" for col in columns])
        placeholders = ", ".join(["%s"] * len(columns))
        insert_query = f"INSERT INTO {TABLE_NAME} ({columns_sql}) VALUES ({placeholders})"
        
        # Opsional: Menghapus data lama sebelum memasukkan data baru
        cursor.execute(f"DELETE FROM {TABLE_NAME}")

        # L: Load (Memasukkan data secara massal menggunakan executemany)
        data_to_insert = [tuple(row) for row in df.values]
        
        cursor.executemany(insert_query, data_to_insert)
        
        # Komit perubahan ke database
        conn.commit()
        
        print(f"\n✅ Berhasil memasukkan {cursor.rowcount} baris data ke tabel '{TABLE_NAME}'.")

    except FileNotFoundError:
        print(f"\n❌ Kesalahan: File '{CSV_FILE}' tidak ditemukan.")
    except Error as err:
        # Menggunakan 'Error' dari mysql.connector untuk menangkap masalah koneksi/SQL
        print(f"\n❌ Kesalahan MySQL: {err}")
    except Exception as e:
        print(f"\n❌ Terjadi kesalahan tak terduga: {e}")
    finally:
        # Tutup koneksi
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("Koneksi MySQL ditutup.")

# Jalankan fungsi utama
if __name__ == "__main__":
    load_data_to_mysql()