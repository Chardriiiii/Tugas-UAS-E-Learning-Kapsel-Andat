from fastapi import APIRouter, HTTPException
from modules.database import students_db

router = APIRouter()

@router.delete("/{student_id}")
def delete_student(student_id: int):
    global students_db
    students_db = [s for s in students_db if s["id"] != student_id]
    return {"message": f"Student with ID {student_id} has been deleted"}