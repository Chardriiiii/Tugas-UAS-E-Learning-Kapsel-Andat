from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, Float
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from database import get_db, Base, engine
from modules.activities.routes import ActivityModel
from modules.students.routes import EnrollmentModel

router = APIRouter()

# --- MODEL ---
class InteractionLogModel(Base):
    __tablename__ = "interaction_logs"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), index=True)
    activity_id = Column(Integer, index=True) 
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, default=0.0)
    status = Column(String(20), default="in_progress")
    # Score Default None (Null), bukan 0
    score = Column(Float, nullable=True, default=None)

Base.metadata.create_all(bind=engine)

# --- SCHEMAS ---
class StartActivityRequest(BaseModel):
    student_id: str
    activity_id: int 

class StopActivityRequest(BaseModel):
    # Optional, Default None
    score: Optional[float] = None 

class LogResponse(BaseModel):
    id: int = Field(serialization_alias="log_id")
    student_id: str
    activity_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float
    status: str
    
    # UPDATE: Score Optional. Jika None akan muncul 'null' di JSON (bukan 0)
    score: Optional[float] = None
    
    class Config:
        from_attributes = True

# --- HELPER ---
def update_course_progress(db: Session, student_id: str, course_id: int):
    total_activities = db.query(ActivityModel).filter(ActivityModel.course_id == course_id).count()
    if total_activities == 0: return

    completed_count = db.query(InteractionLogModel.activity_id)\
        .join(ActivityModel, InteractionLogModel.activity_id == ActivityModel.id)\
        .filter(
            InteractionLogModel.student_id == student_id,
            InteractionLogModel.status == "completed",
            ActivityModel.course_id == course_id
        ).distinct().count()

    progress_percent = (completed_count / total_activities) * 100

    enrollment = db.query(EnrollmentModel).filter(
        EnrollmentModel.student_id == student_id, EnrollmentModel.course_id == course_id
    ).first()

    if enrollment:
        enrollment.progress = round(progress_percent, 2)
        if progress_percent >= 100:
            enrollment.is_completed = True
            enrollment.completed_at = datetime.now()
        db.commit()

# --- ROUTES ---
@router.post("/start", response_model=LogResponse)
def start_activity(data: StartActivityRequest, db: Session = Depends(get_db)):
    act = db.query(ActivityModel).filter(ActivityModel.id == data.activity_id).first()
    if not act: raise HTTPException(status_code=404, detail="Activity ID tidak ditemukan.")

    is_enrolled = db.query(EnrollmentModel).filter(
        EnrollmentModel.student_id == data.student_id, EnrollmentModel.course_id == act.course_id
    ).first()
    if not is_enrolled: raise HTTPException(status_code=403, detail="Anda belum mengambil mata kuliah ini.")

    # Score default None saat start
    new_log = InteractionLogModel(
        student_id=data.student_id, activity_id=data.activity_id,
        start_time=datetime.now(), status="in_progress", score=None 
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

@router.put("/{id}/stop", response_model=LogResponse)
def stop_activity(id: int, req: StopActivityRequest, db: Session = Depends(get_db)):
    log = db.query(InteractionLogModel).filter(InteractionLogModel.id == id).first()
    if not log: raise HTTPException(status_code=404, detail="Log tidak ditemukan.")
    if log.status == "completed": raise HTTPException(status_code=400, detail="Sesi ini sudah selesai.")

    log.end_time = datetime.now()
    log.duration_seconds = (log.end_time - log.start_time).total_seconds()
    log.status = "completed"
    
    # UPDATE: Hanya update score jika user mengirim nilai (tidak None)
    if req.score is not None: 
        log.score = req.score
    # Jika req.score None, biarkan log.score tetap None
    
    db.commit()
    
    activity = db.query(ActivityModel).filter(ActivityModel.id == log.activity_id).first()
    if activity: update_course_progress(db, log.student_id, activity.course_id)

    db.refresh(log)
    return log

@router.get("/", response_model=List[LogResponse])
def get_logs(student_id: str = None, db: Session = Depends(get_db)):
    query = db.query(InteractionLogModel)
    if student_id: query = query.filter(InteractionLogModel.student_id == student_id)
    return query.all()