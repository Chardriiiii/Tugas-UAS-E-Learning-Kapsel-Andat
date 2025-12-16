import csv
import os
from sqlalchemy.orm import Session
from database.database import engine, Base # Impor Absolut
from database.models import StudentPerformance # Impor Absolut

def seed_students_data():
    """
    Membaca file CSV dan memasukkan data ke tabel students_performance.
    """
    print("Mengecek dan mereset struktur tabel...")
    
    # 🛑 PERBAIKAN UNTUK DUPLICATE ENTRY: Hapus tabel lama, lalu buat baru
    Base.metadata.drop_all(bind=engine, tables=[StudentPerformance.__table__]) 
    Base.metadata.create_all(bind=engine) 

    # 2. Definisikan jalur CSV (menggunakan jalur relatif robust yang sudah benar)
    base_path = os.path.abspath(os.path.dirname(__file__))
    csv_file_path = os.path.join(
        os.path.dirname(base_path), # Root folder proyek
        'data', 
        'Students Performance Dataset.csv'
    )
    
    db = Session(bind=engine)
    print("Memulai proses seeding...")

    # Peta kolom CSV ke atribut Model Python
    column_mapping = {
        'Student_ID': 'Student_ID', 'First_Name': 'First_Name', 'Last_Name': 'Last_Name', 
        'Email': 'Email', 'Gender': 'Gender', 'Age': 'Age', 'Department': 'Department', 
        'Attendance (%)': 'Attendance_Percentage', 'Midterm_Score': 'Midterm_Score', 
        'Final_Score': 'Final_Score', 'Assignments_Avg': 'Assignments_Avg', 
        'Quizzes_Avg': 'Quizzes_Avg', 'Participation_Score': 'Participation_Score', 
        'Projects_Score': 'Projects_Score', 'Total_Score': 'Total_Score', 'Grade': 'Grade', 
        'Study_Hours_per_Week': 'Study_Hours_per_Week', 'Extracurricular_Activities': 'Extracurricular_Activities', 
        'Internet_Access_at_Home': 'Internet_Access_at_Home', 'Parent_Education_Level': 'Parent_Education_Level', 
        'Family_Income_Level': 'Family_Income_Level', 'Stress_Level (1-10)': 'Stress_Level', 
        'Sleep_Hours_per_Night': 'Sleep_Hours_per_Night',
    }
    
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            records_to_insert = []
            
            for row in csv_reader:
                student_data = {}
                is_valid = True
                
                for csv_col, model_attr in column_mapping.items():
                    value = row.get(csv_col)
                    
                    try:
                        if model_attr in ['Attendance_Percentage', 'Midterm_Score', 'Final_Score', 'Assignments_Avg', 'Quizzes_Avg', 'Participation_Score', 'Projects_Score', 'Total_Score', 'Study_Hours_per_Week', 'Sleep_Hours_per_Night']:
                            # Konversi ke float, tangani nilai kosong
                            student_data[model_attr] = float(value) if value and value.strip() else None
                        elif model_attr in ['Age', 'Stress_Level']:
                            # Konversi ke integer, tangani nilai kosong
                            student_data[model_attr] = int(value) if value and value.strip() else None
                        else:
                            student_data[model_attr] = value
                    except ValueError:
                        is_valid = False
                        # PENTING: Jika ada data numerik yang tidak valid, baris tersebut diabaikan
                        break 
                
                if is_valid:
                    records_to_insert.append(StudentPerformance(**student_data))

            if records_to_insert:
                # Menggunakan add_all untuk efisiensi Bulk Insert
                db.add_all(records_to_insert)
                db.commit()
                print(f"Seeding berhasil! Total {len(records_to_insert)} records dimasukkan.")
            else:
                 print("Tidak ada record yang valid untuk dimasukkan.")


    except FileNotFoundError:
        db.rollback()
        print(f"❌ ERROR: File CSV tidak ditemukan di path: {csv_file_path}")
        print("\nPastikan folder 'data' ada di root proyek Anda.")
    except Exception as e:
        db.rollback()
        print(f"Seeding GAGAL pada tahap koneksi/transaksi! Error: {e}")
        print("Pastikan server MySQL berjalan, kredensial di .env sudah benar, dan koneksi ke database Anda terbuka.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_students_data()