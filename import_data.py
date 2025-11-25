import pandas as pd
from sqlalchemy import create_engine

# --- 1. KONFIGURASI DATABASE & FILE (SESUAIKAN DI SINI) ---
db_user = 'root'             # Username MySQL (default: root)
db_pass = 'Babikambing1'      # <--- GANTI dengan password MySQL Workbench Anda
db_host = 'localhost'
db_port = '3306'
db_name = 'student_performance_db'  # <--- Sudah disesuaikan

# Ganti 'nama_file_anda.csv' dengan nama file csv yang sebenarnya
# Jika file csv ada di satu folder yang sama dengan file python ini, hapus 'data/'
csv_file_path = 'data/Students Performance Dataset.csv' 

# Nama tabel yang ingin dibuat di MySQL nanti
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

    # (Opsional) Membersihkan nama kolom (mengganti spasi dengan underscore)
    # Ini penting agar query SQL tidak error nantinya
    df.columns = [c.strip().replace(' ', '_').lower() for c in df.columns]

    # 4. Mengirim Data ke MySQL
    print(f"🚀 Sedang mengupload {len(df)} baris data...")
    
    # if_exists='replace' -> Kalau tabel sudah ada, hapus dan buat baru
    # if_exists='append'  -> Kalau tabel sudah ada, tambahkan data di bawahnya
    df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)

    print("🎉 SUKSES! Dataset berhasil masuk ke MySQL Workbench.")
    print(f"   Silakan cek tabel '{table_name}' di database '{db_name}'.")

except FileNotFoundError:
    print(f"❌ ERROR: File tidak ditemukan di path '{csv_file_path}'.")
    print("   Pastikan nama file dan folder sudah benar.")
except Exception as e:
    print(f"❌ ERROR Lainnya: {e}")