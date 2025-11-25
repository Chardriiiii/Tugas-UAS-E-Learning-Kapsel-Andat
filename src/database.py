import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="nmqWFd3lmviUcx6K",
        database="students_performance_db"
    )