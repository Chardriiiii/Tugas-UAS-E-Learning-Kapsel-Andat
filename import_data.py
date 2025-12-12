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

DEFAULT_COURSES = [
    {"course_name": "Calculus 1", "department": "Mathematics", "credits": 4},
    {"course_name": "Data Structures", "department": "CS", "credits": 4},
    {"course_name": "Macroeconomics", "department": "Business", "credits": 3},
]

DEFAULT_ACTIVITIES = [
    # Calculus
    {"name": "Video: Intro to Limits", "type": "Video", "course_id": 1},
    {"name": "Quiz: Derivatives", "type": "Quiz", "course_id": 1},
    # CS
    {"name": "Video: Linked Lists", "type": "Video", "course_id": 2},
    {"name": "Forum: Big O Notation", "type": "Forum", "course_id": 2},
]

def fix_database_and_import():
    try:
        print("🔄 Menghubungkan ke MySQL...")
        with engine.connect() as conn:
            # RESET TOTAL
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

        # 1. ISI COURSES
        course_map = {}
        for c in DEFAULT_COURSES:
            new_c = CourseModel(**c)
            db.add(new_c)
            db.commit()
            db.refresh(new_c)
            course_map[new_c.department] = new_c.id 

        # 2. ISI ACTIVITIES
        for a in DEFAULT_ACTIVITIES:
            db.add(ActivityModel(**a))
        db.commit()

        # 3. IMPORT MAHASISWA
        print(f"📂 Import Mahasiswa...")
        df = pd.read_csv(csv_file_path)
        
        # Cleaning Data
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
                # Default Progress 0
                enrollments.append(EnrollmentModel(student_id=s.student_id, course_id=c_id, progress=0.0))
        
        if enrollments:
            db.add_all(enrollments)
            db.commit()

        db.close()
        print("🎉 Database Siap! Fitur Progress Tracking sudah aktif.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_database_and_import()