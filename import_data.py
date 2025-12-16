import pandas as pd
import random
from sqlalchemy import create_engine, text
from database import engine, Base, SessionLocal

# --- IMPORT MODELS ---
try:
    # Update Import: Tambahkan PrerequisiteModel
    from modules.courses.routes import CourseModel, PrerequisiteModel
    from modules.activities.routes import ActivityModel
    from modules.interaction_logs.routes import InteractionLogModel
    from modules.students.routes import StudentModel, EnrollmentModel
except ImportError as e:
    print(f"⚠️ Note: {e}")

# --- KONFIGURASI ---
csv_file_path = 'data/Students Performance Dataset.csv'
table_name = 'student_scores'

DEFAULT_COURSES_WITH_ACTIVITIES = [
    {
        "course_name": "Calculus 1",
        "department": "Mathematics",
        "credits": 4,
        "activities": [
            {"name": "Video: Introduction to Limits", "type": "Video"},
            {"name": "Quiz: Derivatives Basic", "type": "Quiz"},
            {"name": "Midterm Exam: Integration", "type": "Exam"}
        ]
    },
    {
        "course_name": "Data Structures",
        "department": "CS",
        "credits": 4,
        "activities": [
            {"name": "Video: Linked Lists vs Arrays", "type": "Video"},
            {"name": "Assignment: Build a Binary Tree", "type": "Assignment"},
            {"name": "Forum: Big O Notation Discussion", "type": "Forum"}
        ]
    },
    {
        "course_name": "Macroeconomics",
        "department": "Business",
        "credits": 3,
        "activities": [
            {"name": "Lecture: Supply and Demand", "type": "Lecture"},
            {"name": "Case Study: Market Failures", "type": "Assignment"},
            {"name": "Quiz: Fiscal Policy", "type": "Quiz"}
        ]
    },
    {
        "course_name": "Physics 101",
        "department": "Engineering",
        "credits": 4,
        "activities": [
            {"name": "Lab: Newton's Laws", "type": "Lab"},
            {"name": "Simulation: Projectile Motion", "type": "Interactive"},
            {"name": "Final Project: Bridge Design", "type": "Project"}
        ]
    },
]

# Helper: Tentukan Grade berdasarkan Score
def calculate_grade(score):
    if score >= 85: return "A"
    elif score >= 70: return "B"
    elif score >= 55: return "C"
    elif score >= 40: return "D"
    return "E"

def fix_database_and_import():
    try:
        print("🔄 Menghubungkan ke MySQL...")
        with engine.connect() as conn:
            # RESET DB
            conn.execute(text("DROP TABLE IF EXISTS prerequisites")) # Drop tabel prasyarat
            conn.execute(text("DROP TABLE IF EXISTS certificates"))
            conn.execute(text("DROP TABLE IF EXISTS enrollments"))
            conn.execute(text("DROP TABLE IF EXISTS interaction_logs"))
            conn.execute(text("DROP TABLE IF EXISTS activity_logs"))
            conn.execute(text("DROP TABLE IF EXISTS activities"))
            conn.execute(text("DROP TABLE IF EXISTS courses"))
            conn.commit()
        
        print("🏗️  Membuat tabel baru...")
        Base.metadata.create_all(bind=engine)
        
        db = SessionLocal()

        # 1. ISI COURSES & ACTIVITIES
        print("🏗️  Membuat Courses dan Default Activities...")
        course_map = {}
        
        for data in DEFAULT_COURSES_WITH_ACTIVITIES:
            activities_data = data.pop("activities")
            new_course = CourseModel(**data)
            db.add(new_course)
            db.commit()
            db.refresh(new_course)
            course_map[new_course.department] = new_course.id
            
            for act in activities_data:
                new_activity = ActivityModel(
                    name=act["name"],
                    type=act["type"],
                    course_id=new_course.id
                )
                db.add(new_activity)
        db.commit()

        # ==========================================
        # 🆕 INSERT DATA PRASYARAT SIMULASI
        # ==========================================
        print("🔗 Menghubungkan Prerequisite (Kalkulus 2 butuh Kalkulus 1)...")
        
        # Cari Calculus 1 (yg baru dibuat)
        calc1 = db.query(CourseModel).filter(CourseModel.course_name == "Calculus 1").first()
        
        if calc1:
            # Buat Course Calculus 2
            calc2 = CourseModel(course_name="Calculus 2", department="Mathematics", credits=4)
            db.add(calc2)
            db.commit()
            db.refresh(calc2)
            
            # Buat Aturan: Calc 2 butuh Calc 1
            rule = PrerequisiteModel(course_id=calc2.id, prereq_id=calc1.id)
            db.add(rule)
            db.commit()
            print(f"   -> Aturan dibuat: {calc2.course_name} (ID: {calc2.id}) syaratnya {calc1.course_name} (ID: {calc1.id})")
        
        # 3. IMPORT MAHASISWA & SIMULASI DATA
        print(f"📂 Import Mahasiswa & Generating Mock Data...")
        df = pd.read_csv(csv_file_path)
        
        # Cleaning Data Standard
        df.columns = [c.strip().replace(' ', '_').replace('(', '').replace(')', '').replace('%', '').lower() for c in df.columns]
        cols_drop = ['email', 'parent_education_level', 'family_income_level', 'sleep_hours_per_night']
        df.drop(columns=[c for c in cols_drop if c in df.columns], inplace=True)
        
        if 'attendance_' in df.columns: df = df[df['attendance_'] > 70]
        if 'first_name' in df.columns and 'last_name' in df.columns:
            df['full_name'] = df['first_name'] + ' ' + df['last_name']
            df.drop(columns=['first_name', 'last_name'], inplace=True)

        # --- LOGIKA BARU: SIMULASI CAMPURAN (MIXED DATA) ---
        for index, row in df.iterrows():
            # 40% Peluang Mahasiswa sudah Lulus (Completed)
            is_graduated = random.random() < 0.4
            
            if is_graduated:
                simulated_score = round(random.uniform(50, 100), 2)
                simulated_grade = calculate_grade(simulated_score)
                
                df.at[index, 'total_score'] = simulated_score
                df.at[index, 'grade'] = simulated_grade
                df.at[index, 'attendance_'] = round(random.uniform(75, 100), 2)
            else:
                df.at[index, 'total_score'] = 0.0
                df.at[index, 'grade'] = None 
                df.at[index, 'attendance_'] = 0.0

       # Simpan Student Profile ke DB
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)

        # ======================================================
        # 🛠️ PERBAIKAN: RESTART SESSION
        # Kita harus refresh koneksi karena tabel baru saja di-drop/replace oleh Pandas
        db.close()       # Tutup sesi lama
        db = SessionLocal() # Buka sesi baru
        # ======================================================

        # 4. AUTO ENROLL & SYNC STATUS
        print("   -> Auto Enroll & Sync Progress...")
        students = db.query(StudentModel).all()
        enrollments = []
        
        for s in students:
            if s.department in course_map:
                c_id = course_map[s.department]
                
                # Logic Auto-Enroll
                if s.grade is not None:
                    enrollments.append(EnrollmentModel(
                        student_id=s.student_id,
                        course_id=c_id,
                        progress=100.0,           
                        is_completed=True,        
                        final_score=s.total_score,
                        grade=s.grade             
                    ))
                else:
                    enrollments.append(EnrollmentModel(
                        student_id=s.student_id,
                        course_id=c_id,
                        progress=0.0,             
                        is_completed=False,
                        final_score=None,
                        grade=None
                    ))
        
        if enrollments:
            db.add_all(enrollments)
            db.commit()
        
        db.close()
        print("🎉 Database Siap! Data sudah dicampur (40% Completed, 60% In Progress).")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_database_and_import()