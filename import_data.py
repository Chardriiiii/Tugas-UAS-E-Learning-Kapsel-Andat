import pandas as pd
import sys
import os
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# --- 1. SETUP DATABASE & MODEL (LANGSUNG DI SINI) ---
print("--- MULAI SCRIPT IMPORT (VERSI ANTI-GAGAL) ---")

load_dotenv() # Baca .env

# Pastikan settingan database dibaca
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

if not db_name:
    print("❌ ERROR: File .env tidak terbaca atau kosong. Pastikan file .env ada.")
    sys.exit(1)

# Buat koneksi
DATABASE_URL = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definisi Tabel (Kita tulis ulang disini biar pasti terbaca)
class StudentModel(Base):
    __tablename__ = "students_performance"

    id = Column(Integer, primary_key=True, index=True)
    student_id_csv = Column(String(50), index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(150))
    gender = Column(String(20), index=True)
    age = Column(Integer)
    department = Column(String(100), index=True)
    attendance_pct = Column(Float)
    midterm_score = Column(Float)
    final_score = Column(Float)
    assignments_avg = Column(Float)
    quizzes_avg = Column(Float)
    participation_score = Column(Float)
    projects_score = Column(Float)
    total_score = Column(Float, index=True)
    grade = Column(String(5), index=True)
    study_hours_week = Column(Float)
    extracurricular = Column(String(100))
    internet_access = Column(String(10))
    parent_education = Column(String(100))
    family_income = Column(String(100))
    stress_level = Column(Integer)
    sleep_hours_night = Column(Float)

# --- 2. PAKSA BUAT TABEL ---
try:
    print(f"Target Database: {db_name}")
    print("Mereset tabel lama & membuat baru...")
    Base.metadata.drop_all(bind=engine)   # Hapus tabel lama (jika ada sisa error)
    Base.metadata.create_all(bind=engine) # Buat tabel baru
    print("✅ Tabel 'students_performance' BERHASIL dibuat!")
except Exception as e:
    print(f"❌ GAGAL KONEKSI KE DATABASE: {e}")
    print("Tips: Cek apakah XAMPP (MySQL) sudah nyala? Cek isi file .env?")
    sys.exit(1)

# --- 3. BACA CSV & IMPORT ---
csv_file = "Students Performance Dataset.csv"

def safe_float(val):
    try:
        return float(val) if val is not None else 0.0
    except:
        return 0.0

def safe_int(val):
    try:
        return int(val) if val is not None else 0
    except:
        return 0

try:
    df = pd.read_csv(csv_file)
    print(f"✅ Membaca CSV: {len(df)} baris data.")
    
    df.columns = df.columns.str.strip()
    df = df.where(pd.notnull(df), None)

    db = SessionLocal()
    count = 0
    print("⏳ Sedang memasukkan data...")

    for index, row in df.iterrows():
        student = StudentModel(
            student_id_csv = str(row['Student_ID']),
            first_name = row['First_Name'],
            last_name = row['Last_Name'],
            email = row['Email'],
            gender = row['Gender'],
            age = safe_int(row['Age']),
            department = row['Department'],
            attendance_pct = safe_float(row['Attendance (%)']), 
            midterm_score = safe_float(row['Midterm_Score']),
            final_score = safe_float(row['Final_Score']),
            assignments_avg = safe_float(row['Assignments_Avg']),
            quizzes_avg = safe_float(row['Quizzes_Avg']),
            participation_score = safe_float(row['Participation_Score']),
            projects_score = safe_float(row['Projects_Score']),
            total_score = safe_float(row['Total_Score']),
            grade = row['Grade'],
            study_hours_week = safe_float(row['Study_Hours_per_Week']),
            extracurricular = row['Extracurricular_Activities'],
            internet_access = row['Internet_Access_at_Home'],
            parent_education = row['Parent_Education_Level'],
            family_income = row['Family_Income_Level'],
            stress_level = safe_int(row['Stress_Level (1-10)']),
            sleep_hours_night = safe_float(row['Sleep_Hours_per_Night'])
        )
        db.add(student)
        count += 1
        
        if count % 100 == 0:
            print(f"   > {count} data masuk...")

    db.commit()
    print(f"🎉 SUKSES BESAR! {count} data telah masuk ke database.")

except FileNotFoundError:
    print(f"❌ File CSV '{csv_file}' tidak ditemukan di folder ini.")
except Exception as e:
    print(f"❌ ERROR SAAT IMPORT: {e}")
    db.rollback()
finally:
    db.close()