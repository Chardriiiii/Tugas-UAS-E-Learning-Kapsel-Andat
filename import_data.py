import pandas as pd
from sqlalchemy import create_engine, text
from database import engine, Base, SessionLocal

# --- IMPORT MODELS ---
try:
    from modules.courses.routes import CourseModel
<<<<<<< HEAD
    from modules.activities.routes import ActivityModel 
    from modules.interaction_logs.routes import InteractionLogModel
    from modules.students.routes import StudentModel, EnrollmentModel
except ImportError as e:
    print(f"⚠️ Note: {e}")
=======
    from modules.activity_logs.routes import ActivityLogModel
    from modules.students.routes import StudentModel
except ImportError as e:
    print(f"⚠️ Warning: Gagal import model ({e}). Pastikan struktur folder benar.")
>>>>>>> c20463b35a8d886f254c1a5445aa1b0b1e7056a1

# --- KONFIGURASI ---
csv_file_path = 'data/Students Performance Dataset.csv'
table_name = 'student_scores'

<<<<<<< HEAD
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
=======
# --- DAFTAR MATA KULIAH DEFAULT (SEED DATA) ---
DEFAULT_COURSES = [
    # --- MATA KULIAH UMUM (Bisa diambil semua jurusan) ---
    {"course_name": "English for Academic Purpose", "department": "General", "credits": 2},
    {"course_name": "Basic Entrepreneurship", "department": "General", "credits": 2},
    {"course_name": "Pancasila & Citizenship", "department": "General", "credits": 2},

    # --- MATHEMATICS ---
    {"course_name": "Calculus 1", "department": "Mathematics", "credits": 4},
    {"course_name": "Linear Algebra", "department": "Mathematics", "credits": 3},
    {"course_name": "Probability Theory", "department": "Mathematics", "credits": 3},

    # --- CS (Computer Science) ---
    {"course_name": "Data Structures & Algo", "department": "CS", "credits": 4},
    {"course_name": "Database Systems", "department": "CS", "credits": 3},
    {"course_name": "Web Development", "department": "CS", "credits": 3},

    # --- ENGINEERING ---
    {"course_name": "Engineering Physics", "department": "Engineering", "credits": 3},
    {"course_name": "Material Science", "department": "Engineering", "credits": 3},
    
    # --- BUSINESS ---
    {"course_name": "Macroeconomics", "department": "Business", "credits": 3},
    {"course_name": "Financial Accounting", "department": "Business", "credits": 3},
]
# ---------------------------------------------------------
>>>>>>> c20463b35a8d886f254c1a5445aa1b0b1e7056a1

def fix_database_and_import():
    try:
        print("🔄 Menghubungkan ke MySQL...")
        with engine.connect() as conn:
<<<<<<< HEAD
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
=======
            print("✅ Terhubung ke database.")

            # 1. BERSIHKAN TABEL LAMA
            print("🛠️  Membersihkan tabel lama...")
            conn.execute(text("DROP TABLE IF EXISTS activities"))
            conn.execute(text("DROP TABLE IF EXISTS activity_logs"))
            conn.execute(text("DROP TABLE IF EXISTS courses"))
            conn.commit()
            print("   -> Tabel lama berhasil dihapus.")

        # 2. BUAT ULANG TABEL
        print("🏗️  Membuat ulang tabel dengan struktur terbaru...")
        Base.metadata.create_all(bind=engine)
        print("   -> Struktur tabel siap.")

        # =========================================================
        # LANGKAH BARU: ISI MATA KULIAH DEFAULT (SEEDING)
        # =========================================================
        print("🌱 Sedang mengisi Default Courses (Matkul Umum & Jurusan)...")
        db = SessionLocal()
        try:
            for course_data in DEFAULT_COURSES:
                new_course = CourseModel(**course_data)
                db.add(new_course)
            db.commit()
            print(f"   -> Sukses menambahkan {len(DEFAULT_COURSES)} mata kuliah default.")
        except Exception as e:
            print(f"   ❌ Gagal mengisi courses: {e}")
            db.rollback()
        finally:
            db.close()

        # 3. IMPORT DATA MAHASISWA CSV
        print(f"📂 Membaca file CSV: {csv_file_path}...")
        df = pd.read_csv(csv_file_path)

        # -- PEMBERSIHAN DATA --
        df.columns = [
            c.strip().replace(' ', '_').replace('(', '').replace(')', '')
            .replace('%', '').replace('-', '_').lower() 
            for c in df.columns
        ]

        cols_to_drop = ['email', 'parent_education_level','sleep_hours_per_night','family_income_level']
        existing_cols = [c for c in cols_to_drop if c in df.columns]
        if existing_cols:
            df.drop(columns=existing_cols, inplace=True)
        
        if 'attendance_' in df.columns:
            df = df[df['attendance_'] > 70]
        
>>>>>>> c20463b35a8d886f254c1a5445aa1b0b1e7056a1
        if 'first_name' in df.columns and 'last_name' in df.columns:
            df['full_name'] = df['first_name'] + ' ' + df['last_name']
            df.drop(columns=['first_name', 'last_name'], inplace=True)

<<<<<<< HEAD
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
=======
        # -- UPLOAD KE MYSQL --
        print(f"🚀 Mengupload {len(df)} data mahasiswa ke tabel '{table_name}'...")
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)

        print("\n🎉🎉 SUKSES! Database Complete (Students + Default Courses).")
        print("Sekarang jalankan: fastapi dev main.py")

    except FileNotFoundError:
        print(f"❌ ERROR: File CSV tidak ditemukan di '{csv_file_path}'")
    except Exception as e:
        print(f"❌ ERROR: {e}")
>>>>>>> c20463b35a8d886f254c1a5445aa1b0b1e7056a1

if __name__ == "__main__":
    fix_database_and_import()