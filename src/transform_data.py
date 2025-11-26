import mysql.connector
import pandas as pd
import os
import sys

# --- MAGIC CODE AGAR BISA IMPORT DARI FOLDER LAIN ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config.database import get_db_connection

# Lokasi CSV
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE_PATH = os.path.join(BASE_DIR, 'assets', 'Students Performance Dataset.csv')

def transform_database():
    print("⚙️  MEMULAI TRANSFORMASI DATABASE...")
    print("   Dari: Data Mentah (23 Kolom)")
    print("   Ke  : Data Bersih (6 Kolom)")
    
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. DROP TABLE LAMA (Hapus tabel gendut)
        print("1️⃣  Menghapus tabel lama...")
        cursor.execute("DROP TABLE IF EXISTS students_performance")

        # 2. CREATE TABLE BARU (Buat tabel langsing)
        print("2️⃣  Membuat struktur tabel baru (hanya kolom penting)...")
        cursor.execute("""
            CREATE TABLE students_performance (
                Student_ID VARCHAR(20) PRIMARY KEY,
                First_Name VARCHAR(50),
                Last_Name VARCHAR(50),
                Department VARCHAR(50),
                Total_Score DECIMAL(5, 2),
                Grade CHAR(1)
            )
        """)

        # 3. ISI ULANG DATA (Hanya ambil kolom penting dari CSV)
        print("3️⃣  Memigrasi data...")
        df = pd.read_csv(CSV_FILE_PATH)
        
        # Query Insert Pendek
        sql = """
            INSERT INTO students_performance 
            (Student_ID, First_Name, Last_Name, Department, Total_Score, Grade) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        val_list = []
        for _, row in df.iterrows():
            val_list.append((
                row['Student_ID'], 
                row['First_Name'], 
                row['Last_Name'], 
                row['Department'], 
                row['Total_Score'], 
                row['Grade']
            ))

        cursor.executemany(sql, val_list)
        conn.commit()
        
        print("------------------------------------------------")
        print(f"✅ TRANSFORMASI SUKSES!")
        print(f"   Sekarang tabel 'students_performance' hanya berisi 6 kolom.")
        print("   Silakan cek di MySQL: SELECT * FROM students_performance;")
        print("------------------------------------------------")

    except Exception as e:
        print(f"❌ Gagal Transformasi: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    transform_database()