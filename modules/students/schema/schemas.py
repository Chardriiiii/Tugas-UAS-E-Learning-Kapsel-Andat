from pydantic import BaseModel
from typing import Optional, Any

# Sesuaikan schema dengan Model baru
class StudentBase(BaseModel):
    student_id_csv: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    department: Optional[str] = None
    parent_education: Optional[str] = None
    total_score: Optional[float] = None
    grade: Optional[str] = None

class Student(StudentBase):
    id: int
    class Config:
        from_attributes = True

class ResponseModel(BaseModel):
    success: bool
    message: str
    data: Any