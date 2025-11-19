# Ini adalah simulasi database menggunakan List Python
# Agar data tersimpan selama server menyala

students_db = [
    {"student_id": 1, "nim": "101", "name": "Budi", "email": "budi@test.com", "password": "123", "role": "student"},
    {"student_id": 2, "nim": "102", "name": "Siti", "email": "siti@test.com", "password": "123", "role": "student"}
]

# Format Log: log_id (unik untuk log), student_id (milik siapa), dll
activity_logs_db = [
    {"log_id": 1, "student_id": 1, "activity_type": "belajar", "duration": 60, "score": 0},
    {"log_id": 2, "student_id": 1, "activity_type": "diskusi", "duration": 30, "score": 80},
    {"log_id": 3, "student_id": 2, "activity_type": "belajar", "duration": 15, "score": 0}, 
]

# Secret key untuk JWT
SECRET_KEY = "rahasia_super_aman"
ALGORITHM = "HS256"