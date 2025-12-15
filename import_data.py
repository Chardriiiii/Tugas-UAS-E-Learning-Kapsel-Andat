import pandas as pd
from sqlalchemy import create_engine, text
from database import engine, Base, SessionLocal

# --- IMPORT MODELS ---
try:
    from modules.courses.routes import CourseModel
    from modules.activities.routes import ActivityModel 
    from modules.interaction_logs.routes import InteractionLogModel
    from modules.students.routes import StudentModel, EnrollmentModel
except ImportError as e:
    print(f"⚠️ Note: {e}")

# --- KONFIGURASI ---
csv_file_path = 'data/Students Performance Dataset.csv'
table_name = 'student_scores'

# 1. UPDATE: Menambahkan Engineering
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
        "department": "Engineering", # <-- Ini penting agar siswa Engineering masuk
        "credits": 4,
        "activities": [
            {"name": "Lab: Newton's Laws", "type": "Lab"},
            {"name": "Simulation: Projectile Motion", "type": "Interactive"},
            {"name": "Final Project: Bridge Design", "type": "Project"}
        ]
    },
]

def fix_database_and_import():
    try:
        print("🔄 Menghubungkan ke MySQL...")
        with engine.connect() as conn:
            # RESET DB
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

        # 1. ISI COURSES & ACTIVITIES SEKALIGUS
        print("🏗️  Membuat Courses dan Default Activities...")
        course_map = {} 
        
        for data in DEFAULT_COURSES_WITH_ACTIVITIES:
            # Pisahkan data activities dari data course agar tidak error saat masuk ke CourseModel
            activities_data = data.pop("activities") 
            
            # Buat Course
            new_course = CourseModel(**data) 
            db.add(new_course)
            db.commit()
            db.refresh(new_course)
            
            # Simpan ID untuk keperluan enroll nanti
            course_map[new_course.department] = new_course.id 
            
            # Buat Activities untuk Course ini
            for act in activities_data:
                new_activity = ActivityModel(
                    name=act["name"],
                    type=act["type"],
                    course_id=new_course.id
                )
                db.add(new_activity)
        
        db.commit()

        # 3. IMPORT MAHASISWA
        print(f"📂 Import Mahasiswa...")
        df = pd.read_csv(csv_file_path)
        
        df.columns = [c.strip().replace(' ', '_').replace('(', '').replace(')', '').replace('%', '').lower() for c in df.columns]
        cols_drop = ['email', 'parent_education_level', 'family_income_level', 'sleep_hours_per_night']
        df.drop(columns=[c for c in cols_drop if c in df.columns], inplace=True)
        if 'attendance_' in df.columns: df = df[df['attendance_'] > 70]
        if 'first_name' in df.columns and 'last_name' in df.columns:
            df['full_name'] = df['first_name'] + ' ' + df['last_name']
            df.drop(columns=['first_name', 'last_name'], inplace=True)

        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)

        # 4. AUTO ENROLL
        print("   -> Auto Enroll Mahasiswa...")
        students = db.query(StudentModel).all()
        enrollments = []
        for s in students:
            if s.department in course_map:
                c_id = course_map[s.department]
                enrollments.append(EnrollmentModel(student_id=s.student_id, course_id=c_id, progress=0.0))
        
        if enrollments:
            db.add_all(enrollments)
            db.commit()

        db.close()
        print("🎉 Database Siap! Engineering Department sudah ditambahkan.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_database_and_import()