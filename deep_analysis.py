import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import numpy as np

# --- KONFIGURASI KONEKSI DATABASE ---
# Ganti password sesuai milik Anda (contoh: "12345" atau "root")
DB_USER = "root"
DB_PASSWORD = "akucldaripalembang"  # <-- Sesuaikan password Anda
DB_HOST = "localhost"
DB_NAME = "student_performance_db"

# Buat koneksi
connection_str = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(connection_str)

print("🚀 Sedang mengambil data dari MySQL...")
query = "SELECT * FROM student_scores"
df = pd.read_sql(query, engine)

print("\n--- DAFTAR NAMA KOLOM ---")
print(df.columns.tolist())
print("-------------------------\n")

# Konversi kolom angka agar aman (Data Cleaning on-the-fly)
numeric_cols = ['total_score', 'study_hours_week', 'stress_level', 'sleep_hours_night', 'attendance_pct']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

print(f"✅ Data siap! Total: {len(df)} mahasiswa.\n")

# ==========================================
# BAB 1: KORELASI (Mencari Hubungan Sebab-Akibat)
# ==========================================
print("📊 Membuat Heatmap Korelasi...")
plt.figure(figsize=(10, 8))

# Kita hanya ambil kolom angka untuk dicek hubungannya
correlation_matrix = df[numeric_cols].corr()

# Gambar Heatmap
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
plt.title('Peta Korelasi: Faktor Apa yang Mempengaruhi Nilai?')
plt.savefig('1_analisis_korelasi.png')
print("   -> Disimpan: 1_analisis_korelasi.png")
# Cara baca: Warna Merah Gelap = Hubungan Kuat. Biru = Hubungan Terbalik.

# ==========================================
# BAB 2: DISTRIBUSI (Jurusan Mana Paling Pintar/Sulit?)
# ==========================================
print("📦 Membuat Boxplot Distribusi Nilai per Jurusan...")
plt.figure(figsize=(12, 6))

# Boxplot menunjukkan sebaran: Nilai minimum, maksimum, dan rata-rata sekaligus
sns.boxplot(x='department', y='total_score', data=df, palette="Set3")
plt.title('Sebaran Nilai Mahasiswa per Departemen')
plt.xlabel('Jurusan')
plt.ylabel('Total Score')
plt.xticks(rotation=45) # Miringkan tulisan jurusan biar terbaca
plt.savefig('2_analisis_distribusi_jurusan.png')
print("   -> Disimpan: 2_analisis_distribusi_jurusan.png")

# ==========================================
# BAB 3: PENGARUH STRES (Apakah Stres Membantu atau Merusak?)
# ==========================================
print("🤯 Membuat Grafik Pengaruh Stres...")
plt.figure(figsize=(10, 6))

# Kita kelompokkan nilai berdasarkan level stres (1-10)
sns.lineplot(x='stress_level', y='total_score', data=df, marker='o', color='red')
plt.title('Hubungan Tingkat Stres vs Rata-rata Nilai')
plt.xlabel('Level Stres (1-10)')
plt.ylabel('Rata-rata Nilai')
plt.grid(True)
plt.savefig('3_analisis_stress_vs_nilai.png')
print("   -> Disimpan: 3_analisis_stress_vs_nilai.png")

# ==========================================
# BAB 4: DETEKSI ANOMALI (Siapa yang butuh bantuan?)
# ==========================================
print("\n🔍 MENCARI MAHASISWA BERISIKO TINGGI (Anomali)...")

# Kriteria: Rajin belajar (jam belajar > rata-rata) TAPI nilainya jelek (< 60)
avg_study = df['study_hours_week'].mean()
berisiko = df[ (df['study_hours_week'] > avg_study) & (df['total_score'] < 60) ]

print(f"Rata-rata jam belajar: {avg_study:.2f} jam/minggu")
print(f"Ditemukan {len(berisiko)} mahasiswa yang 'Rajin tapi Nilai Rendah':")

if not berisiko.empty:
    print(berisiko[['first_name', 'department', 'study_hours_week', 'total_score']].head(10))
    # Simpan daftar ini ke CSV baru untuk dilaporkan ke dosen/BK
    berisiko.to_csv('laporan_mahasiswa_perlu_bimbingan.csv', index=False)
    print("   -> Laporan disimpan: laporan_mahasiswa_perlu_bimbingan.csv")

print("\n✅ ANALISIS MENDALAM SELESAI!")