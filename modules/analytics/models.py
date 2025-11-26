from sqlalchemy import Column, Integer, String, Float
from database import Base

class StudentModel(Base):
    __tablename__ = "students_performance"

    id = Column(Integer, primary_key=True, index=True)
    
    # index=True artinya kolom ini akan dibuatkan "daftar isi" biar cepat dicari
    student_id_csv = Column(String(50), index=True) 
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(150))
    
    # Kita index Gender biar bisa filter: "Tampilkan semua Laki-laki"
    gender = Column(String(20), index=True) 
    age = Column(Integer)

    # Kita index Department biar bisa filter: "Tampilkan anak jurusan Science"
    department = Column(String(100), index=True) 
    attendance_pct = Column(Float)

    midterm_score = Column(Float)
    final_score = Column(Float)
    assignments_avg = Column(Float)
    quizzes_avg = Column(Float)
    participation_score = Column(Float)
    projects_score = Column(Float)
    
    # Kita index Total Score biar bisa filter: "Nilai > 80"
    total_score = Column(Float, index=True) 
    
    # Kita index Grade biar bisa filter: "Cari yang dapat nilai A"
    grade = Column(String(5), index=True)

    study_hours_week = Column(Float)
    extracurricular = Column(String(100))
    internet_access = Column(String(10))
    parent_education = Column(String(100))
    family_income = Column(String(100))
    stress_level = Column(Integer)
    sleep_hours_night = Column(Float)