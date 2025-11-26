-- 1. Membuat Database baru
CREATE DATABASE students_performance_db;

-- 2. Menggunakan Database yang baru dibuat
USE students_performance_db;

-- 3. Membuat Tabel di dalam database tersebut
CREATE TABLE students_performance (
    Student_ID VARCHAR(20),
    First_Name VARCHAR(50),
    Last_Name VARCHAR(50),
    Email VARCHAR(100),
    Gender VARCHAR(10),
    Age INT,
    Department VARCHAR(50),
    Attendance DECIMAL(5, 2),
    Midterm_Score DECIMAL(5, 2),
    Final_Score DECIMAL(5, 2),
    Assignments_Avg DECIMAL(5, 2),
    Quizzes_Avg DECIMAL(5, 2),
    Participation_Score DECIMAL(5, 2),
    Projects_Score DECIMAL(5, 2),
    Total_Score DECIMAL(5, 2),
    Grade CHAR(1),
    Study_Hours_per_Week DECIMAL(5, 2),
    Extracurricular_Activities VARCHAR(3), -- Yes/No
    Internet_Access_at_Home VARCHAR(3),    -- Yes/No
    Parent_Education_Level VARCHAR(50),
    Family_Income_Level VARCHAR(20),
    Stress_Level_1_10 INT,
    Sleep_Hours_per_Night DECIMAL(4, 2)
);

SELECT * FROM students_performance;