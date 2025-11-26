from fastapi import FastAPI
from database import Base, engine
from modules.students.routes import read_students

# Buat tabel di database jika belum ada
Base.metadata.create_all(bind=engine)

# --- BAGIAN PENTING (JANGAN DIHAPUS) ---
app = FastAPI()
# ---------------------------------------

# Hubungkan route siswa ke aplikasi utama
app.include_router(read_students.router)

@app.get("/")
def root():
    return {"message": "Server Berjalan! Buka http://127.0.0.1:8000/docs untuk tes API."}