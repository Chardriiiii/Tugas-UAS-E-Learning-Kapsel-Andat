from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Ganti password sesuai konfigurasi MySQL Anda
<<<<<<< HEAD
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:nmqWFd3lmviUcx6K@localhost:3306/student_performance_db"
=======
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:nmqWFd3lmviUcx6K@localhost:3306/students_performance_db"
>>>>>>> c20463b35a8d886f254c1a5445aa1b0b1e7056a1

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

<<<<<<< HEAD
=======
# Dependency untuk koneksi DB di setiap request
>>>>>>> c20463b35a8d886f254c1a5445aa1b0b1e7056a1
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()