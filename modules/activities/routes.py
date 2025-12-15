from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel, Field
from typing import List
from database import get_db, Base, engine

router = APIRouter()

# --- MODEL DATABASE ---
class ActivityModel(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150))          # Nama materi
    type = Column(String(50))           # Video, Quiz, Forum
    course_id = Column(Integer, index=True) # Relasi ke Course

Base.metadata.create_all(bind=engine)

# --- PYDANTIC SCHEMAS ---
class ActivityBase(BaseModel):
    name: str
    type: str
    course_id: int

class ActivityResponse(ActivityBase):
    id: int = Field(serialization_alias="activity_id")
    class Config:
        from_attributes = True

# --- ROUTES ---
@router.post("/", response_model=ActivityResponse)
def create_activity(
    activity: ActivityBase, 
    db: Session = Depends(get_db),
    x_role: str = Header(default="student")
):
    if x_role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Hanya Admin bisa tambah materi.")
    
    new_act = ActivityModel(**activity.dict())
    db.add(new_act)
    db.commit()
    db.refresh(new_act)
    return new_act

@router.get("/", response_model=List[ActivityResponse])
def get_activities(course_id: int = None, db: Session = Depends(get_db)):
    query = db.query(ActivityModel)
    if course_id:
        query = query.filter(ActivityModel.course_id == course_id)
    return query.all()