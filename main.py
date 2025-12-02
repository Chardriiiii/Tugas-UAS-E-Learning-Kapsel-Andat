from fastapi import FastAPI
import uvicorn

# Import Routes
from modules.students import routes as student_routes
from modules.courses import routes as course_routes
from modules.activity_logs import routes as log_routes
from modules.activity_logs import analytics

app = FastAPI(
    title="E-Learning Activity Tracker API",
    description="Project 3: Student Performance & Analytics (No Auth)",
    version="1.0.0"
)

# Register Routers
app.include_router(student_routes.router, prefix="/students", tags=["Students"])
app.include_router(course_routes.router, prefix="/courses", tags=["Courses"])
app.include_router(log_routes.router, prefix="/activities", tags=["Activity Logs (CRUD)"])
app.include_router(analytics.router, prefix="/analytics", tags=["Data Analysis"])

@app.get("/")
def root():
    return {"message": "API Running. Access /docs for Swagger."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)