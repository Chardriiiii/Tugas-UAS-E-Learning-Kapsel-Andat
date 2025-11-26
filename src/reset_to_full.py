import mysql.connector
import pandas as pd
import os
import sys

# Magic Code untuk import database
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config.database import get_db_connection

# Lokasi CSV
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE_PATH = os.path.join(BASE_DIR, 'assets', 'Students Performance Dataset.csv')

def reset_database():
    print("🔄 MEMULAI PROSES RESET DATABASE (UNDO)...")
    print("   Target: Kembali ke Data Lengkap (23 Kolom)")
    
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()

    try:
        # 1. Hapus Tabel Lama (yang cuma 6 kolom)
        print("1️⃣  Menghapus tabel saat ini...")
        cursor.execute("DROP TABLE IF EXISTS students_performance")

        # 2. Buat Ulang Tabel LENGKAP (23 Kolom)
        print("2️⃣  Membuat ulang struktur tabel LENGKAP...")
        cursor.execute("""
            CREATE TABLE students_performance (
                Student_ID VARCHAR(20) PRIMARY KEY,
                First_Name VARCHAR(50),
                Last_Name VARCHAR(50),
                Email VARCHAR(100),
                Gender VARCHAR(10),
                Age INT,
                Department VARCHAR(50),
                Attendance DECIMAL(5, 2),
                Midterm_Score DECIMAL(5, 2),
                Final_Score DECIMAL(5, 2),
                Assignments_Avg DECIMAL(5, 2),
                Quizzes_Avg DECIMAL(5, 2),
                Participation_Score DECIMAL(5, 2),
                Projects_Score DECIMAL(5, 2),
                Total_Score DECIMAL(5, 2),
                Grade CHAR(1),
                Study_Hours_per_Week DECIMAL(5, 2),
                Extracurricular_Activities VARCHAR(3),
                Internet_Access_at_Home VARCHAR(3),
                Parent_Education_Level VARCHAR(50),
                Family_Income_Level VARCHAR(20),
                Stress_Level_1_10 INT,
                Sleep_Hours_per_Night DECIMAL(4, 2)
            )
        """)

        # 3. Masukkan Data CSV Lagi
        print("3️⃣  Memasukkan ulang semua data...")
        df = pd.read_csv(CSV_FILE_PATH)
        df = df.where(pd.notnull(df), None) # Handle NaN

        # Query Insert Panjang
        sql = """
            INSERT INTO students_performance 
            (Student_ID, First_Name, Last_Name, Email, Gender, Age, Department, Attendance, 
             Midterm_Score, Final_Score, Assignments_Avg, Quizzes_Avg, Participation_Score, 
             Projects_Score, Total_Score, Grade, Study_Hours_per_Week, Extracurricular_Activities, 
             Internet_Access_at_Home, Parent_Education_Level, Family_Income_Level, 
             Stress_Level_1_10, Sleep_Hours_per_Night) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        val_list = []
        for _, row in df.iterrows():
            val_list.append((
                row['Student_ID'], row['First_Name'], row['Last_Name'], row['Email'], row['Gender'], 
                row['Age'], row['Department'], row['Attendance (%)'], row['Midterm_Score'], 
                row['Final_Score'], row['Assignments_Avg'], row['Quizzes_Avg'], 
                row['Participation_Score'], row['Projects_Score'], row['Total_Score'], row['Grade'], 
                row['Study_Hours_per_Week'], row['Extracurricular_Activities'], 
                row['Internet_Access_at_Home'], row['Parent_Education_Level'], 
                row['Family_Income_Level'], row['Stress_Level (1-10)'], row['Sleep_Hours_per_Night']
            ))

        cursor.executemany(sql, val_list)
        conn.commit()
        
        print("------------------------------------------------")
        print(f"✅ RESET BERHASIL!")
        print(f"   Database kembali gendut (23 Kolom).")
        print("------------------------------------------------")

    except Exception as e:
        print(f"❌ Gagal Reset: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    reset_database()