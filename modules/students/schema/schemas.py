from pydantic import BaseModel, EmailStr
from typing import Optional

class StudentBase(BaseModel):
    nim: str
    name: str
    email: EmailStr

class StudentCreate(StudentBase):
    password: str

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

# PERHATIKAN BAGIAN INI
class StudentResponse(StudentBase):
    student_id: int  # <--- Pastikan ini student_id, BUKAN id
    role: str
    
    class Config:
        from_attributes = True