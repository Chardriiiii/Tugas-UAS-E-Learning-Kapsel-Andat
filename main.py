from fastapi import FastAPI

# Import Routes dari masing-masing modul
from modules.auth.routes import login
from modules.students.routes import createStudent, readStudent, updateStudent, deleteStudent
from modules.activity_logs.routes import createLog, readLog

app = FastAPI(
    title="E-Learning Activity Tracker API",
    description="Project 3: Project 3: E-Learning Activity Tracker",
    version="1.0.0"
)

# 1. Register Auth Routes
app.include_router(login.router, prefix="/auth", tags=["Authentication"])

# 2. Register Student Routes (CRUD Terpisah)
app.include_router(createStudent.router, prefix="/students", tags=["Students"])
app.include_router(readStudent.router, prefix="/students", tags=["Students"])
app.include_router(updateStudent.router, prefix="/students", tags=["Students"])
app.include_router(deleteStudent.router, prefix="/students", tags=["Students"])

# 3. Register Activity/Logs Routes (Termasuk Analisis)
app.include_router(createLog.router, prefix="/activities", tags=["Activities"])
app.include_router(readLog.router, prefix="/activities", tags=["Activities & Analytics"])

@app.get("/")
def root():
    return {"message": "E-Learning API is running. Go to /docs for Swagger UI."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)