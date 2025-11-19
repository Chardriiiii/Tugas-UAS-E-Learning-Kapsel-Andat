from fastapi import APIRouter, Depends
from typing import List
from modules.students.schema.schemas import StudentResponse
from modules.database import students_db

router = APIRouter()

@router.get("/", response_model=List[StudentResponse])
def read_all_students():
    return students_db

@router.get("/{student_id}", response_model=StudentResponse)
def read_student_by_id(student_id: int):
    student = next((s for s in students_db if s["id"] == student_id), None)
    if not student:
        return {} # Bisa ditambahkan raise HTTPException
    return student