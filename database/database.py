# database/database.py

import os
from dotenv import load_dotenv 
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Muat variabel lingkungan dari file .env (Mencari di root folder)
load_dotenv() 

# --- 1. Konfigurasi Koneksi Database dari .env ---
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# 🛑 Pengecekan Wajib untuk Mencegah ValueError: 'None' 🛑
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise ValueError(
        "Koneksi Database GAGAL! Pastikan file .env ada di ROOT folder dan berisi:\n"
        "DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, dan DB_NAME."
    )

# Bentuk URL koneksi
SQLALCHEMY_DATABASE_URL = (
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# --- 2. Membuat Engine (Mesin Koneksi) ---
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True
)

# --- 3. SessionLocal, Base, dan get_db ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()