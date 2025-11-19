from pydantic import BaseModel

class LogCreate(BaseModel):
    student_id: int     # Merujuk ke mahasiswa
    activity_type: str  # Contoh: 'belajar', 'diskusi'
    duration: int       # Menit
    score: int = 0      

class LogResponse(LogCreate):
    log_id: int         # <--- NAMA BARU (Jelas dan Tidak Ambigu)

    class Config:
        from_attributes = True