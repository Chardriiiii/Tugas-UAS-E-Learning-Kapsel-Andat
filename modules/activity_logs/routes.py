from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime
from pydantic import BaseModel
from datetime import datetime
from typing import List
from database import get_db, Base, engine

router = APIRouter()

class ActivityLogModel(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), index=True)
    activity_type = Column(String(50))
    description = Column(String(255))
    timestamp = Column(DateTime, default=datetime.now)

Base.metadata.create_all(bind=engine)

class LogCreate(BaseModel):
    student_id: str
    activity_type: str
    description: str

class LogResponse(LogCreate):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True  # <--- UPDATE DISINI (V2)

@router.post("/", response_model=LogResponse)
def create_log(log: LogCreate, db: Session = Depends(get_db)):
    new_log = ActivityLogModel(**log.dict())
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

@router.get("/", response_model=List[LogResponse])
def read_logs(student_id: str = None, db: Session = Depends(get_db)):
    query = db.query(ActivityLogModel)
    if student_id:
        query = query.filter(ActivityLogModel.student_id == student_id)
    return query.all()