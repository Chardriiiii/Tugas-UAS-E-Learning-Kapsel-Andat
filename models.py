from sqlalchemy import Column, Integer, String, Float
from database import Base

class StudentModel(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id_csv = Column(String(50))  # Untuk kolom 'Student_ID'
    first_name = Column(String(50))      # Untuk kolom 'First_Name'
    last_name = Column(String(50))       # Untuk kolom 'Last_Name'
    email = Column(String(100))          # Untuk kolom 'Email'
    gender = Column(String(20))          # Untuk kolom 'Gender'
    department = Column(String(100))     # Untuk kolom 'Department'
    parent_education = Column(String(100)) # Untuk 'Parent_Education_Level'
    total_score = Column(Float)          # Untuk 'Total_Score'
    grade = Column(String(10))           # Untuk 'Grade'