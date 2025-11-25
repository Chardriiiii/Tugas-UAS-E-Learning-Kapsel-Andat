from fastapi import APIRouter, HTTPException
from modules.students.schema.schemas import StudentUpdate, StudentResponse
from modules.database import students_db

router = APIRouter()

@router.put("/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student_update: StudentUpdate):
    # Cari index mahasiswa berdasarkan student_id
    # Perhatikan kita sekarang pakai "student_id", BUKAN "id"
    idx = next((i for i, item in enumerate(students_db) if item["student_id"] == student_id), None)
    
    if idx is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Update data
    current_data = students_db[idx]
    update_data = student_update.dict(exclude_unset=True)
    
    updated_student = {**current_data, **update_data}
    students_db[idx] = updated_student
    
    return updated_student