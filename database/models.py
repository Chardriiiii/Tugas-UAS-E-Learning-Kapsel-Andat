from sqlalchemy import Column, Integer, String, Float, Enum
from database.database import Base # Impor absolut

class StudentPerformance(Base):
    __tablename__ = "students_performance"

    # Definisi Kolom
    Student_ID = Column(String(10), primary_key=True, index=True)
    First_Name = Column(String(50), nullable=False)
    Last_Name = Column(String(50), nullable=False)
    Email = Column(String(100), unique=True)
    Gender = Column(Enum('Male', 'Female'), nullable=False)
    Age = Column(Integer)
    Department = Column(String(50))
    Attendance_Percentage = Column("Attendance_Percentage (%)", Float(5, 2))
    Midterm_Score = Column(Float(5, 2))
    Final_Score = Column(Float(5, 2))
    Assignments_Avg = Column(Float(5, 2))
    Quizzes_Avg = Column(Float(5, 2))
    Participation_Score = Column(Float(5, 2))
    Projects_Score = Column(Float(5, 2))
    Total_Score = Column(Float(7, 4))
    Grade = Column(Enum('A', 'B', 'C', 'D', 'F'))
    Study_Hours_per_Week = Column(Float(4, 1))
    Extracurricular_Activities = Column(Enum('Yes', 'No'))
    Internet_Access_at_Home = Column(Enum('Yes', 'No'))
    Parent_Education_Level = Column(String(50))
    Family_Income_Level = Column(Enum('Low', 'Medium', 'High'))
    Stress_Level = Column("Stress_Level (1-10)", Integer)
    Sleep_Hours_per_Night = Column(Float(3, 1))

    def __repr__(self):
        return f"<Student(id={self.Student_ID}, name='{self.First_Name} {self.Last_Name}')>"