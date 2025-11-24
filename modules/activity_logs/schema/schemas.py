from pydantic import BaseModel
from typing import Optional

class LogCreate(BaseModel):
    student_id: int
    activity_type: str
    duration: int
    
    # PERUBAHAN DI SINI:
    # Menggunakan 'None' artinya secara default datanya 'null' (kosong/tidak ada)
    # Bukan 0.
    score: Optional[int] = None 

class LogResponse(LogCreate):
    log_id: int

    class Config:
        from_attributes = True