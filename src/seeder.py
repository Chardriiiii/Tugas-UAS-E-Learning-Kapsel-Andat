import pandas as pd
import os
import sys

# Trik agar bisa import file database.py di folder yang sama
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import database 

# Lokasi file CSV (naik satu folder dari src, lalu masuk assets)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE_PATH = os.path.join(BASE_DIR, 'assets', 'Students Performance Dataset.csv')

def seed_data():
    print("🚀 Memulai proses seeding...")
    
    # Cek koneksi database dulu
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        print("✅ Koneksi database berhasil.")
    except Exception as e:
        print(f"❌ Gagal koneksi database: {e}")
        return

    # Baca CSV
    if not os.path.exists(CSV_FILE_PATH):
        print(f"❌ File CSV tidak ditemukan di: {CSV_FILE_PATH}")
        return

    try:
        df = pd.read_csv(CSV_FILE_PATH)
        # Ubah NaN (kosong) menjadi None agar dianggap NULL oleh MySQL
        df = df.where(pd.notnull(df), None)
        
        print(f"📂 Berhasil membaca {len(df)} baris data.")

        # Query SQL
        sql = """
            INSERT INTO students_performance 
            (Student_ID, First_Name, Last_Name, Email, Gender, Age, Department, Attendance, 
             Midterm_Score, Final_Score, Assignments_Avg, Quizzes_Avg, Participation_Score, 
             Projects_Score, Total_Score, Grade, Study_Hours_per_Week, Extracurricular_Activities, 
             Internet_Access_at_Home, Parent_Education_Level, Family_Income_Level, 
             Stress_Level_1_10, Sleep_Hours_per_Night) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Konversi Dataframe ke List of Tuples untuk Insert
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

        # Eksekusi Batch (Cepat)
        cursor.executemany(sql, val_list)
        conn.commit()
        
        print(f"🎉 SUKSES! {cursor.rowcount} data telah masuk ke database.")

    except Exception as err:
        print(f"❌ Terjadi Error saat insert: {err}")
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_data()