import sys
import os

# --- MAGIC CODE MULAI ---
# Ini memaksa Python untuk mengenali folder project utama
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# --- MAGIC CODE SELESAI ---

from flask import Flask
from src.routes.student_routes import student_bp

app = Flask(__name__)

# Register Routes
app.register_blueprint(student_bp, url_prefix='/api')

@app.route('/')
def index():
    return "<h1>UAS API Running</h1><p>Access /api/students</p>"

if __name__ == '__main__':
    app.run(debug=True, port=5000)