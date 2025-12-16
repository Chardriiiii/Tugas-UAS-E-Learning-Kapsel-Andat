import streamlit as st
import requests
import pandas as pd
import time

# Konfigurasi Halaman
st.set_page_config(
    page_title="Student AI Dashboard",
    page_icon="🎓",
    layout="wide"
)

# URL API Flask (Pastikan app.py jalan di port 5001)
API_URL = "http://127.0.0.1:5001"

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3426/3426653.png", width=100)
    st.title("Menu Analisis")
    menu = st.radio("Pilih Fitur:", ["🏠 Dashboard", "🤖 Prediksi Nilai (AI)", "📊 Clustering Siswa", "📈 Visualisasi Data"])
    
    st.info("Aplikasi ini terhubung ke API Flask yang memiliki kemampuan Machine Learning.")

# --- HALAMAN 1: DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("🎓 Sistem Monitoring Performa Mahasiswa")
    st.markdown("Selamat datang di panel kontrol eksekutif.")
    
    # Ambil data dari API
    try:
        res = requests.get(f"{API_URL}/dashboard/summary")
        if res.status_code == 200:
            data = res.json()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Mahasiswa", data['Total Mahasiswa'], "👤")
            col2.metric("Rata-rata Kampus", data['Rata-rata Nilai'], "⭐")
            col3.metric("Status Server", data['Status'], "✅")
        else:
            st.error("Gagal mengambil data ringkasan.")
    except:
        st.error("API Error: Pastikan app.py sudah dijalankan!")

# --- HALAMAN 2: AI PREDIKSI ---
elif menu == "🤖 Prediksi Nilai (AI)":
    st.title("🤖 AI Grade Predictor")
    st.write("Masukkan jam belajar, AI akan menebak nilai ujian Anda.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        jam = st.number_input("Jam Belajar (per Minggu):", min_value=0, max_value=100, value=10)
        if st.button("Ramal Nilai Saya!"):
            with st.spinner('AI sedang berpikir...'):
                time.sleep(1) # Efek dramatis
                try:
                    res = requests.get(f"{API_URL}/ai/prediksi-nilai?jam_belajar={jam}")
                    hasil = res.json()
                    
                    st.success("Prediksi Selesai!")
                    st.metric("Prediksi Nilai Akhir", hasil['Prediksi Nilai Akhir'])
                    st.info(f"💡 Analisis AI: {hasil['Analisis AI']}")
                except:
                    st.error("Koneksi ke API terputus.")

# --- HALAMAN 3: CLUSTERING ---
elif menu == "📊 Clustering Siswa":
    st.title("🧠 AI Clustering (Pengelompokan Otomatis)")
    st.write("AI membagi siswa menjadi 3 tipe karakter berdasarkan pola belajar.")
    
    if st.button("Jalankan K-Means Clustering"):
        try:
            # Tampilkan Gambar dari API
            st.image(f"{API_URL}/ai/clustering", caption="Hasil Clustering K-Means", use_column_width=True)
            st.success("Grafik di atas digenerate secara real-time oleh server.")
        except:
            st.error("Gagal memuat gambar.")

# --- HALAMAN 4: VISUALISASI ---
elif menu == "📈 Visualisasi Data":
    st.title("📈 Visualisasi Lanjutan")
    
    tab1, tab2, tab3 = st.tabs(["Regresi Linear", "Kesenjangan Jurusan", "Heatmap"])
    
    with tab1:
        st.header("Bukti Hubungan Belajar & Nilai")
        st.image(f"{API_URL}/visualisasi/regresi")
        
    with tab2:
        st.header("Analisis Gap per Jurusan")
        st.image(f"{API_URL}/visualisasi/kesenjangan")

    with tab3:
        st.header("Korelasi Antar Variabel")
        st.image(f"{API_URL}/visualisasi/heatmap")