from flask import jsonify, request
from src.config.database import get_db_connection

# --- LOGIKA FILTERING (PENTING UNTUK UAS) ---
# Di sinilah kita menentukan "kacamata" API.
# Meskipun Database punya 23 kolom, API hanya akan menampilkan kolom-kolom ini
# saat user meminta seluruh data.
IMPORTANT_COLUMNS = "Student_ID, First_Name, Last_Name, Department, Total_Score, Grade, Attendance"

# 1. GET ALL STUDENTS (Menampilkan Data Filter/Ringkas)
def get_students():
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Koneksi database gagal"}), 500

    cursor = conn.cursor(dictionary=True)
    
    try:
        # Kita gunakan variable IMPORTANT_COLUMNS agar outputnya rapi
        query = f"SELECT {IMPORTANT_COLUMNS} FROM students_performance LIMIT 100"
        cursor.execute(query)
        results = cursor.fetchall()
        
        return jsonify({
            "status": "success",
            "message": "Data difilter: Menampilkan kolom utama saja",
            "total_shown": len(results),
            "data": results
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# 2. GET STUDENT BY ID (Menampilkan Data FULL DETAIL)
# Skenario: Jika user klik satu mahasiswa, baru kita buka semua data (SELECT *)
def get_student_by_id(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Ambil SEMUA kolom (23 kolom) karena ini detail view
        cursor.execute("SELECT * FROM students_performance WHERE Student_ID = %s", (student_id,))
        result = cursor.fetchone()
        
        if result:
            return jsonify({
                "status": "success", 
                "message": "Detail lengkap mahasiswa ditemukan",
                "data": result
            }), 200
        else:
            return jsonify({"status": "error", "message": "Mahasiswa tidak ditemukan"}), 404
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# 3. POST (Tambah Data Baru)
# User cukup input data penting saja, sisanya akan NULL di database
def create_student():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        INSERT INTO students_performance 
        (Student_ID, First_Name, Last_Name, Department, Total_Score, Grade)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    # Gunakan .get() agar tidak error jika data kosong (default 0 atau string kosong)
    values = (
        data.get('Student_ID'), 
        data.get('First_Name'), 
        data.get('Last_Name'), 
        data.get('Department'), 
        data.get('Total_Score', 0), 
        data.get('Grade'),
        data.get('Attendance', 0)
    )
    
    try:
        cursor.execute(query, values)
        conn.commit()
        response = jsonify({"status": "success", "message": "Data berhasil disimpan"}), 201
    except Exception as e:
        response = jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
    return response

# 4. PUT (Update Data)
# Fokus update nilai dan absensi
def update_student(student_id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        UPDATE students_performance 
        SET Total_Score = %s, Grade = %s, Attendance = %s
        WHERE Student_ID = %s
    """
    
    values = (
        data.get('Total_Score'), 
        data.get('Grade'), 
        data.get('Attendance'), 
        student_id
    )
    
    try:
        cursor.execute(query, values)
        conn.commit()
        
        if cursor.rowcount == 0:
            response = jsonify({"status": "error", "message": "ID tidak ditemukan"}), 404
        else:
            response = jsonify({"status": "success", "message": "Data berhasil diperbarui"}), 200
            
    except Exception as e:
        conn.rollback()
        response = jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return response

# 5. DELETE (Hapus Data)
def delete_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM students_performance WHERE Student_ID = %s", (student_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            response = jsonify({"status": "error", "message": "ID tidak ditemukan"}), 404
        else:
            response = jsonify({"status": "success", "message": "Data berhasil dihapus"}), 200
            
    except Exception as e:
        conn.rollback()
        response = jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
    return response