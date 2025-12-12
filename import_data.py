import pandas as pd
from sqlalchemy import create_engine, text
from database import engine, Base, SessionLocal

# --- IMPORT MODELS ---
try:
    from modules.courses.routes import CourseModel
    from modules.activity_logs.routes import ActivityLogModel
    from modules.students.routes import StudentModel
except ImportError as e:
    print(f"⚠️ Warning: Gagal import model ({e}). Pastikan struktur folder benar.")

# --- KONFIGURASI ---
csv_file_path = 'data/Students Performance Dataset.csv'
table_name = 'student_scores'

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

def fix_database_and_import():
    try:
        print("🔄 Menghubungkan ke MySQL...")
        with engine.connect() as conn:
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
        
        if 'first_name' in df.columns and 'last_name' in df.columns:
            df['full_name'] = df['first_name'] + ' ' + df['last_name']
            df.drop(columns=['first_name', 'last_name'], inplace=True)

        # -- UPLOAD KE MYSQL --
        print(f"🚀 Mengupload {len(df)} data mahasiswa ke tabel '{table_name}'...")
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)

        print("\n🎉🎉 SUKSES! Database Complete (Students + Default Courses).")
        print("Sekarang jalankan: fastapi dev main.py")

    except FileNotFoundError:
        print(f"❌ ERROR: File CSV tidak ditemukan di '{csv_file_path}'")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    fix_database_and_import()