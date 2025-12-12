from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Ganti password sesuai konfigurasi MySQL Anda
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:nmqWFd3lmviUcx6K@localhost:3306/students_performance_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency untuk koneksi DB di setiap request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()