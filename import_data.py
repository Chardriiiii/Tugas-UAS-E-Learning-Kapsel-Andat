import pandas as pd
import sys
import numpy as np # Kita perlu ini, tapi pandas biasanya sudah cukup pintar
from database import SessionLocal, engine, Base
from models import StudentModel

print("--- MULAI SCRIPT IMPORT BARU (FIXED NAN) ---")

# 1. Buat tabel
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tabel database berhasil dibuat.")
except Exception as e:
    print(f"❌ GAGAL BUAT TABEL: {e}")
    sys.exit(1)

# 2. Baca CSV & Bersihkan Data
csv_file = "Students Performance Dataset.csv"
try:
    df = pd.read_csv(csv_file)
    print(f"✅ Berhasil membaca CSV: {len(df)} baris.")
    
    # --- BAGIAN FIX PENTING ---
    # Mengganti semua NaN (Not a Number) menjadi None agar bisa diterima MySQL sebagai NULL
    df = df.where(pd.notnull(df), None)
    print("✅ Berhasil membersihkan data kosong (NaN -> None).")
    # --------------------------

except Exception as e:
    print(f"❌ GAGAL BACA CSV: {e}")
    sys.exit(1)

# 3. Masukkan Data
db = SessionLocal()
try:
    print("⏳ Sedang memasukkan data ke MySQL (mohon tunggu)...")
    
    count = 0
    for index, row in df.iterrows():
        student = StudentModel(
            student_id_csv = str(row['Student_ID']),
            first_name = row['First_Name'],
            last_name = row['Last_Name'],
            email = row['Email'],
            gender = row['Gender'],
            department = row['Department'],
            parent_education = row['Parent_Education_Level'],
            total_score = row['Total_Score'] if row['Total_Score'] is not None else 0.0, # Jaga-jaga jika nilai kosong
            grade = row['Grade']
        )
        db.add(student)
        count += 1
        
        if count % 500 == 0:
            print(f"   > {count} data diproses...")

    db.commit()
    print("🎉 SUKSES! Semua data berhasil masuk ke MySQL.")

except Exception as e:
    print(f"❌ ERROR SAAT INSERT: {e}")
    db.rollback()
finally:
    db.close()