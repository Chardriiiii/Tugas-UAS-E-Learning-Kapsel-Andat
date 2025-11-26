import pandas as pd
from sqlalchemy import create_engine

# --- 1. KONFIGURASI DATABASE & FILE ---
db_user = 'root'
db_pass = 'Babikambing1'
db_host = 'localhost'
db_port = '3306'
db_name = 'student_performance_db'
csv_file_path = 'data/Students Performance Dataset.csv'
table_name = 'student_scores'
# ---------------------------------------------------------

try:
    # 2. Membuat Koneksi ke MySQL
    print("🔄 Menghubungkan ke MySQL...")
    connection_str = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_str)
    print(f"✅ Terhubung ke database: {db_name}")

    # 3. Membaca File CSV
    print(f"📂 Membaca file: {csv_file_path}...")
    df = pd.read_csv(csv_file_path)

    # PEMBERSIHAN NAMA KOLOM (Penting untuk SQL)
    # Logika: 
    # 1. strip() -> hapus spasi di awal/akhir
    # 2. replace -> ganti spasi dengan underscore
    # 3. replace -> Hapus tanda kurung () dan % agar nama kolom di SQL bersih
    # 4. lower() -> jadi huruf kecil semua
    df.columns = [
        c.strip()
        .replace(' ', '_')
        .replace('(', '')
        .replace(')', '')
        .replace('%', '')
        .replace('-', '_')
        .lower() 
        for c in df.columns
    ]
    # Hasil nama kolom nanti jadi: 'attendance_', 'stress_level_1_10', 'midterm_score', dll.

    # ========================================================================
    # AREA MANIPULASI DATA (Disesuaikan dengan Kolom Kamu)
    # ========================================================================
    print("🛠️  Sedang melakukan manipulasi data...")

    # CONTOH 1: Menghapus Kolom Sensitif/Tidak Perlu
    # Kita hapus 'email' dan 'parent_education_level' agar tabel lebih ringkas
    cols_to_drop = ['email', 'parent_education_level','sleep_hours_per_night','family_income_level']
    # Cek dulu apakah kolom ada agar tidak error
    existing_cols_to_drop = [c for c in cols_to_drop if c in df.columns]
    if existing_cols_to_drop:
        df = df.drop(columns=existing_cols_to_drop)
        print(f"   -> Kolom dihapus: {existing_cols_to_drop}")

    # CONTOH 2: Filter Baris (Misal: Cari mahasiswa yang perlu perhatian)
    # Kita hanya ambil mahasiswa yang 'attendance_' di bawah 70% ATAU 'stress_level' di atas 8
    # (Pastikan nama kolom sesuai hasil pembersihan di atas)
    if 'attendance_' in df.columns:
        # Contoh: Saya hanya ingin import data mahasiswa yang kehadirannya BAGUS (> 80)
        df = df[df['attendance_'] > 70]
        print(f"   -> Filter Data: Hanya mahasiswa dengan kehadiran > 80%. Sisa {len(df)} baris.")

    # CONTOH 3: Membuat Kolom Baru (Manipulasi String)
    # Menggabungkan First Name dan Last Name menjadi 'full_name'
    if 'first_name' in df.columns and 'last_name' in df.columns:
        df['full_name'] = df['first_name'] + ' ' + df['last_name']
        
        # Setelah digabung, kita hapus kolom first dan last name agar tidak duplikat (opsional)
        df = df.drop(columns=['first_name', 'last_name'])
        print("   -> Kolom 'full_name' berhasil dibuat (First & Last name digabung).")

    # ========================================================================
    # SELESAI MANIPULASI
    # ========================================================================

    # 4. Mengirim Data ke MySQL
    print(f"🚀 Sedang mengupload {len(df)} baris data hasil manipulasi...")
    
    df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)

    print("🎉 SUKSES! Dataset masuk ke MySQL.")
    print(f"   Silakan cek tabel '{table_name}' di database '{db_name}'.")

except FileNotFoundError:
    print(f"❌ ERROR: File CSV tidak ditemukan di path '{csv_file_path}'.")
except Exception as e:
    print(f"❌ ERROR Lainnya: {e}")