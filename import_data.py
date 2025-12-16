import pandas as pd
import random
from sqlalchemy import create_engine, text
from database import engine, Base, SessionLocal
from datetime import datetime

# --- IMPORT MODELS ---
try:
    from modules.courses.routes import CourseModel
    from modules.activities.routes import ActivityModel
    from modules.interaction_logs.routes import InteractionLogModel
    from modules.students.routes import StudentModel, EnrollmentModel
except ImportError as e:
    print(f"⚠️ Note: {e}")

csv_file_path = 'data/Students Performance Dataset.csv'
table_name = 'student_scores'

DEFAULT_COURSES_WITH_ACTIVITIES = [
    {
        "course_name": "Calculus 1", "department": "Mathematics", "credits": 4,
        "activities": [
            {"name": "Video: Introduction to Limits", "type": "Video"},
            {"name": "Quiz: Derivatives Basic", "type": "Quiz"},
            {"name": "Midterm Exam: Integration", "type": "Exam"}
        ]
    },
    {
        "course_name": "Data Structures", "department": "CS", "credits": 4,
        "activities": [
            {"name": "Video: Linked Lists vs Arrays", "type": "Video"},
            {"name": "Assignment: Build a Binary Tree", "type": "Assignment"},
            {"name": "Forum: Big O Notation Discussion", "type": "Forum"}
        ]
    },
    {
        "course_name": "Macroeconomics", "department": "Business", "credits": 3,
        "activities": [
            {"name": "Lecture: Supply and Demand", "type": "Lecture"},
            {"name": "Case Study: Market Failures", "type": "Assignment"},
            {"name": "Quiz: Fiscal Policy", "type": "Quiz"}
        ]
    },
    {
        "course_name": "Physics 101", "department": "Engineering", "credits": 4,
        "activities": [
            {"name": "Lab: Newton's Laws", "type": "Lab"},
            {"name": "Simulation: Projectile Motion", "type": "Interactive"},
            {"name": "Final Project: Bridge Design", "type": "Project"}
        ]
    },
]

def calculate_grade(score):
    if score >= 85: return "A"
    elif score >= 70: return "B"
    elif score >= 55: return "C"
    elif score >= 40: return "D"
    return "E"

def fix_database_and_import():
    try:
        print("🔄 Menghubungkan ke MySQL & Resetting tables...")
        with engine.connect() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            tables = ["certificates", "enrollments", "interaction_logs", "activities", "courses"]
            for t in tables:
                conn.execute(text(f"DROP TABLE IF EXISTS {t}"))
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            conn.commit()

        print("🏗️ Membuat tabel baru...")
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()

        print("🏗️ Membuat Courses dan Activities...")
        course_map = {}
        for data in DEFAULT_COURSES_WITH_ACTIVITIES:
            acts = data.pop("activities")
            new_course = CourseModel(**data)
            db.add(new_course)
            db.commit()
            db.refresh(new_course)
            course_map[new_course.department] = new_course.id
            
            for act in acts:
                db.add(ActivityModel(name=act["name"], type=act["type"], course_id=new_course.id))
        db.commit()

        print("📂 Import Mahasiswa & Generating Mock Logs...")
        df = pd.read_csv(csv_file_path)
        df.columns = [c.strip().replace(' ', '_').lower() for c in df.columns]
        if 'first_name' in df.columns and 'last_name' in df.columns:
            df['full_name'] = df['first_name'] + ' ' + df['last_name']
        
        # Simpan profile dasar ke MySQL
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)

        students = db.query(StudentModel).all()
        enrollments = []

        for s in students:
            if s.department in course_map:
                c_id = course_map[s.department]
                is_graduated = random.random() < 0.4 # 40% sudah lulus

                if is_graduated:
                    # Ambil aktivitas matkul ini untuk buat log
                    course_acts = db.query(ActivityModel).filter(ActivityModel.course_id == c_id).all()
                    scores_for_avg = []
                    
                    for act in course_acts:
                        score_val = None
                        # Video tidak ada skor
                        if act.type.lower() not in ["video", "lecture", "forum"]:
                            score_val = round(random.uniform(65, 100), 2)
                            scores_for_avg.append(score_val)
                        
                        db.add(InteractionLogModel(
                            student_id=s.student_id, activity_id=act.id,
                            start_time=datetime.now(), end_time=datetime.now(),
                            status="completed", score=score_val
                        ))
                    
                    final_avg = sum(scores_for_avg) / len(scores_for_avg) if scores_for_avg else 0
                    enrollments.append(EnrollmentModel(
                        student_id=s.student_id, course_id=c_id, progress=100.0,
                        is_completed=True, final_score=final_avg, grade=calculate_grade(final_avg)
                    ))
                else:
                    enrollments.append(EnrollmentModel(
                        student_id=s.student_id, course_id=c_id, progress=0.0,
                        is_completed=False, final_score=None, grade=None
                    ))
        
        db.add_all(enrollments)
        db.commit()
        db.close()
        print("🎉 Selesai! Data log dan rata-rata nilai telah disinkronkan.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_database_and_import()