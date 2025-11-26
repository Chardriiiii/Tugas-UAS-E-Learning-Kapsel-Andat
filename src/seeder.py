import pandas as pd
import os
import sys
from config.database import get_db_connection

# Setup lokasi file CSV
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE_PATH = os.path.join(BASE_DIR, 'assets', 'Students Performance Dataset.csv')

def seed_data():
    print("🚀 Memulai proses seeding data LENGKAP...")
    
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()

    if not os.path.exists(CSV_FILE_PATH):
        print("❌ File CSV tidak ditemukan di folder assets.")
        return

    try:
        # Bersihkan data lama
        cursor.execute("TRUNCATE TABLE students_performance")
        
        # Baca CSV
        df = pd.read_csv(CSV_FILE_PATH)
        df = df.where(pd.notnull(df), None) # Handle data kosong

        # Insert Query untuk 23 Kolom
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
        print(f"🎉 SUKSES! {cursor.rowcount} data lengkap berhasil disimpan.")

    except Exception as err:
        print(f"❌ Error Seeding: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_data()