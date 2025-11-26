import mysql.connector
import pandas as pd
import os
import sys

# Magic Code Import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config.database import get_db_connection

# Lokasi CSV
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE_PATH = os.path.join(BASE_DIR, 'assets', 'Students Performance Dataset.csv')

def transform_attendance():
    print("🎓 MEMULAI TRANSFORMASI: FILTER MAHASISWA RAJIN (Attendance >= 80)...")
    
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()

    try:
        # 1. DROP TABLE LAMA
        print("1️⃣  Menghapus tabel lama...")
        cursor.execute("DROP TABLE IF EXISTS students_performance")

        # 2. CREATE TABLE BARU (Kita tambah kolom Attendance biar bisa dibuktikan)
        print("2️⃣  Membuat tabel baru (Hanya kolom penting + Attendance)...")
        cursor.execute("""
            CREATE TABLE students_performance (
                Student_ID VARCHAR(20) PRIMARY KEY,
                First_Name VARCHAR(50),
                Last_Name VARCHAR(50),
                Department VARCHAR(50),
                Total_Score DECIMAL(5, 2),
                Grade CHAR(1),
                Attendance DECIMAL(5, 2)
            )
        """)

        # 3. BACA & FILTER DATA DI PYTHON
        print("3️⃣  Membaca CSV & Memfilter Data...")
        df = pd.read_csv(CSV_FILE_PATH)
        
        # --- BAGIAN PENTING: FILTER ROW ---
        # "Ambil data dimana kolom 'Attendance (%)' >= 80"
        jumlah_awal = len(df)
        df_filtered = df[df['Attendance (%)'] >= 80] 
        jumlah_akhir = len(df_filtered)
        
        print(f"   📉 Data Awal : {jumlah_awal} baris")
        print(f"   ✅ Data Akhir: {jumlah_akhir} baris (Mahasiswa Rajin)")

        # 4. INSERT DATA
        print("4️⃣  Memasukkan data ke database...")
        sql = """
            INSERT INTO students_performance 
            (Student_ID, First_Name, Last_Name, Department, Total_Score, Grade, Attendance) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        val_list = []
        for _, row in df_filtered.iterrows():
            val_list.append((
                row['Student_ID'], 
                row['First_Name'], 
                row['Last_Name'], 
                row['Department'], 
                row['Total_Score'], 
                row['Grade'],
                row['Attendance (%)']
            ))

        cursor.executemany(sql, val_list)
        conn.commit()
        
        print("------------------------------------------------")
        print(f"🎉 SUKSES! Database sekarang hanya berisi Mahasiswa dengan Absensi >= 80.")
        print("   Silakan cek di MySQL.")
        print("------------------------------------------------")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    transform_attendance()