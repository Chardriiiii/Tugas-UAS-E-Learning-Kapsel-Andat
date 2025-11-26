from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
from pathlib import Path

# --- BAGIAN PERBAIKAN ---
# Cari file .env secara eksplisit
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Cek apakah variabel berhasil dimuat?
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Validasi Error: Jika salah satu kosong, program akan memberitahu
if not DB_PORT:
    print("❌ ERROR: File .env tidak terbaca atau kosong!")
    print(f"Lokasi yang dicari: {env_path}")
    print("Pastikan file bernama '.env' (bukan .env.txt) ada di folder tersebut.")
    # Fallback sementara (agar tidak crash, tapi tetap cek .env ya!)
    DB_HOST = "localhost"
    DB_PORT = "3306"
    DB_USER = "root"
    DB_NAME = "students_db" 
    # Password tetap harus dari .env atau diisi manual di sini jika darurat

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()