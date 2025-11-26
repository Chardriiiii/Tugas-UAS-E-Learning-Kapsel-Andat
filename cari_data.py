from database import SessionLocal
from modules.analytics.models import StudentModel
from sqlalchemy import or_

# 1. Buka Koneksi ke MySQL
db = SessionLocal()

print("--- ALAT PENCARI DATA MAHASISWA ---")
print("Biarkan kosong jika tidak ingin memfilter bagian tersebut.")

# 2. Input Filter dari Pengguna (Lewat Terminal)
input_jurusan = input("Masukkan Jurusan (contoh: Science/Arts): ").strip()
input_grade = input("Masukkan Grade (contoh: A/B/C): ").strip()
input_min_score = input("Masukkan Minimal Total Score (contoh: 80): ").strip()

# 3. Mulai Membangun Query (Perintah Pencarian)
# Awalnya kita ambil semua data
query = db.query(StudentModel)

# Jika user isi Jurusan, kita persempit pencarian
if input_jurusan:
    query = query.filter(StudentModel.department == input_jurusan)

# Jika user isi Grade, kita persempit lagi
if input_grade:
    query = query.filter(StudentModel.grade == input_grade)

# Jika user isi Minimal Nilai, kita persempit lagi
if input_min_score:
    try:
        nilai_min = float(input_min_score)
        # Mencari nilai yang LEBIH BESAR atau SAMA DENGAN (>=)
        query = query.filter(StudentModel.total_score >= nilai_min)
    except:
        print("⚠ Peringatan: Input nilai salah, filter nilai diabaikan.")

# 4. Jalankan Query (Ambil Data)
# .limit(20) agar terminal tidak penuh (ambil 20 saja)
hasil = query.limit(20).all()

# 5. Tampilkan Hasil
print(f"\n--- DITEMUKAN {len(hasil)} DATA (Menampilkan max 20) ---")

if not hasil:
    print("Tidak ada data yang cocok dengan kriteria tersebut.")
else:
    print(f"{'ID':<10} | {'NAMA DEPAN':<15} | {'JURUSAN':<15} | {'GRADE':<5} | {'SCORE'}")
    print("-" * 65)
    for siswa in hasil:
        print(f"{siswa.student_id_csv:<10} | {siswa.first_name:<15} | {siswa.department:<15} | {siswa.grade:<5} | {siswa.total_score}")

db.close()