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

class StudentResponse(StudentBase):
    student_id: int   # <--- UBAH DARI 'id' MENJADI 'student_id'
    role: str