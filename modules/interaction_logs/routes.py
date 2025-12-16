from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, Float, func
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional
from database import get_db, Base, engine
from modules.activities.routes import ActivityModel
from modules.students.routes import EnrollmentModel

router = APIRouter()

# --- MODEL DATABASE ---
class InteractionLogModel(Base):
    __tablename__ = "interaction_logs"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), index=True)
    activity_id = Column(Integer, index=True)
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, default=0.0)
    status = Column(String(20), default="in_progress")
    score = Column(Float, nullable=True, default=None)

Base.metadata.create_all(bind=engine)

# --- PYDANTIC SCHEMAS ---
class StartActivityRequest(BaseModel):
    student_id: str
    activity_id: int

class StopActivityRequest(BaseModel):
    score: Optional[float] = None

    @field_validator('score')
    def validate_score_range(cls, v):
        if v is not None:
            if v < 0 or v > 100:
                raise ValueError("Skor harus berada pada rentang 0 sampai 100.")
        return v

class LogResponse(BaseModel):
    id: int = Field(serialization_alias="log_id")
    student_id: str
    activity_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float
    status: str
    score: Optional[float] = None

    class Config:
        from_attributes = True

# --- HELPER: UPDATE PROGRESS & GRADE ---
def update_course_progress(db: Session, student_id: str, course_id: int):
    # Hitung total materi dalam matkul
    total_activities = db.query(ActivityModel).filter(ActivityModel.course_id == course_id).count()
    if total_activities == 0: return

    # Hitung log yang selesai
    completed_logs = db.query(InteractionLogModel)\
        .join(ActivityModel, InteractionLogModel.activity_id == ActivityModel.id)\
        .filter(
            InteractionLogModel.student_id == student_id,
            InteractionLogModel.status == "completed",
            ActivityModel.course_id == course_id
        ).all()

    unique_acts = set([log.activity_id for log in completed_logs])
    progress_percent = (len(unique_acts) / total_activities) * 100

    # Hitung rata-rata skor
    scores = [log.score for log in completed_logs if log.score is not None]
    avg_score = sum(scores) / len(scores) if scores else 0.0

    enrollment = db.query(EnrollmentModel).filter(
        EnrollmentModel.student_id == student_id, EnrollmentModel.course_id == course_id
    ).first()

    if enrollment:
        enrollment.progress = round(progress_percent, 2)
        enrollment.final_score = round(avg_score, 2)
        
        # Jika progress turun di bawah 100% karena ada log yang dihapus
        if progress_percent < 100:
            enrollment.is_completed = False
            enrollment.grade = "Course in Progress"
        else:
            enrollment.is_completed = True
            enrollment.completed_at = datetime.now()
            if avg_score >= 85: enrollment.grade = "A"
            elif avg_score >= 70: enrollment.grade = "B"
            elif avg_score >= 55: enrollment.grade = "C"
            elif avg_score >= 40: enrollment.grade = "D"
            else: enrollment.grade = "E"
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

    new_log = InteractionLogModel(
        student_id=data.student_id, activity_id=data.activity_id,
        start_time=datetime.now(), status="in_progress", score=None
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

@router.put("/{log_id}/stop", response_model=LogResponse)
def stop_activity(log_id: int, req: StopActivityRequest, db: Session = Depends(get_db)):
    log = db.query(InteractionLogModel).filter(InteractionLogModel.id == log_id).first()
    if not log: raise HTTPException(status_code=404, detail="Log ID tidak ditemukan.")
    if log.status == "completed": raise HTTPException(status_code=400, detail="Sesi sudah selesai.")

    activity = db.query(ActivityModel).filter(ActivityModel.id == log.activity_id).first()
    log.end_time = datetime.now()
    log.duration_seconds = (log.end_time - log.start_time).total_seconds()
    log.status = "completed"

    if activity and activity.type.lower() in ["video", "forum", "lecture"]:
        log.score = None
    else:
        log.score = req.score if req.score is not None else 0.0

    db.commit()
    if activity:
        update_course_progress(db, log.student_id, activity.course_id)
    db.refresh(log)
    return log

@router.delete("/{log_id}")
def delete_log(log_id: int, db: Session = Depends(get_db)):
    # 1. Cari log-nya
    log = db.query(InteractionLogModel).filter(InteractionLogModel.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log ID tidak ditemukan.")

    # 2. Ambil informasi penting sebelum dihapus (untuk update progress nanti)
    student_id = log.student_id
    activity = db.query(ActivityModel).filter(ActivityModel.id == log.activity_id).first()
    course_id = activity.course_id if activity else None

    # 3. Hapus data
    db.delete(log)
    db.commit()

    # 4. Sinkronisasi ulang progress kursus setelah data dihapus
    if course_id:
        update_course_progress(db, student_id, course_id)

    return {"status": "success", "message": f"Log ID {log_id} berhasil dihapus dan progress telah diperbarui."}

@router.get("/", response_model=List[LogResponse])
def get_logs(student_id: str = None, db: Session = Depends(get_db)):
    query = db.query(InteractionLogModel)
    if student_id: query = query.filter(InteractionLogModel.student_id == student_id)
    return query.all()