from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, or_
from pydantic import BaseModel, Field
from typing import List, Optional
from database import get_db, Base, engine

router = APIRouter()

# ==========================
# 1. DATABASE MODEL
# ==========================
class CourseModel(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String(100), nullable=False)
    department = Column(String(50), nullable=True)
    credits = Column(Integer, default=3)

# Pastikan tabel dibuat
Base.metadata.create_all(bind=engine)

# ==========================
# 2. PYDANTIC SCHEMAS
# ==========================
class CourseBase(BaseModel):
    course_name: str
    department: Optional[str] = None
    credits: int = 3

class CourseResponse(CourseBase):
    # Mengubah 'id' database menjadi 'course_id' di JSON response
    id: int = Field(serialization_alias="course_id")
    
    class Config:
        from_attributes = True

# ==========================
# 3. ROUTES
# ==========================

@router.get("/", response_model=List[CourseResponse])
def read_courses(
    department: Optional[str] = None, # Parameter query (misal: ?department=CS)
    db: Session = Depends(get_db)
):
    try:
        query = db.query(CourseModel)
        
        # LOGIKA FILTER:
        # Jika user memasukkan filter department (misal: "Mathematics"),
        # Tampilkan mata kuliah "Mathematics" DAN mata kuliah "General" (seperti English, Pancasila)
        if department:
            query = query.filter(
                or_(
                    CourseModel.department == department,
                    CourseModel.department == "General"
                )
            )
            
        return query.all()
        
    except Exception as e:
        print(f"❌ ERROR GET COURSES: {e}")
        # Kembalikan list kosong jika error, biar frontend tidak crash
        return []

@router.post("/", response_model=CourseResponse)
def create_course(
    course: CourseBase, 
    db: Session = Depends(get_db),
    # Header wajib 'x-role: admin' untuk simulasi hak akses
    x_role: str = Header(default="student", description="Isi 'admin' untuk akses posting")
):
    # Validasi Admin
    if x_role.lower() != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Akses Ditolak: Hanya 'admin' yang boleh menambahkan mata kuliah."
        )

    try:
        new_course = CourseModel(
            course_name=course.course_name,
            department=course.department,
            credits=course.credits
        )
        db.add(new_course)
        db.commit()
        db.refresh(new_course)
        return new_course
    except Exception as e:
        print(f"❌ ERROR POST COURSE: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{course_id}")
def delete_course(
    course_id: int, 
    db: Session = Depends(get_db),
    # Header wajib 'x-role: admin'
    x_role: str = Header(default="student")
):
    # Validasi Admin
    if x_role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Akses Ditolak: Hanya Admin yang boleh menghapus.")

    try:
        course = db.query(CourseModel).filter(CourseModel.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        db.delete(course)
        db.commit()
        return {"message": "Course deleted successfully"}
        
    except Exception as e:
        print(f"❌ ERROR DELETE COURSE: {e}")
        raise HTTPException(status_code=500, detail=str(e))