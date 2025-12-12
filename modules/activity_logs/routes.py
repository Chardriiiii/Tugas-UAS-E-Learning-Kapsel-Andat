from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime
from pydantic import BaseModel, Field # <--- Tambah Import Field
from datetime import datetime
from typing import List, Optional
from database import get_db, Base, engine

from modules.courses.routes import CourseModel

router = APIRouter()

# ==========================
# 1. DATABASE MODEL
# ==========================
class ActivityLogModel(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), index=True)
    course_id = Column(Integer, index=True) 
    activity_type = Column(String(50)) 
    description = Column(String(255))
    timestamp = Column(DateTime, default=datetime.now)

Base.metadata.create_all(bind=engine)

# ==========================
# 2. PYDANTIC SCHEMAS
# ==========================
class LogCreate(BaseModel):
    student_id: str
    course_id: int
    activity_type: str
    description: str

class LogResponse(LogCreate):
    # Mengubah 'id' menjadi 'log_id' di tampilan JSON
    id: int = Field(serialization_alias="log_id") 
    
    timestamp: datetime
    class Config:
        from_attributes = True

# ==========================
# 3. ROUTES
# ==========================
@router.post("/", response_model=LogResponse)
def create_log(log: LogCreate, db: Session = Depends(get_db)):
    # Validasi Course
    course_exists = db.query(CourseModel).filter(CourseModel.id == log.course_id).first()
    if not course_exists:
        raise HTTPException(status_code=400, detail=f"Error: Course ID {log.course_id} tidak ditemukan.")

    new_log = ActivityLogModel(**log.dict())
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

@router.get("/", response_model=List[LogResponse])
def read_logs(student_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(ActivityLogModel)
    if student_id:
        query = query.filter(ActivityLogModel.student_id == student_id)
    return query.all()