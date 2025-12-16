from fastapi import FastAPI
import uvicorn

# Import Routes
from modules.students import routes as student_routes
from modules.courses import routes as course_routes
from modules.activities import routes as activity_routes
from modules.interaction_logs import routes as tracking_routes
from modules.interaction_logs import analytics

app = FastAPI(
    title="E-Learning Activity Tracker API",
    description="Project 3: With Progress Tracking (No Auth)",
    version="3.1.0"
)

# Register Routers
app.include_router(student_routes.router, prefix="/students", tags=["Students & Enrollment"])
app.include_router(course_routes.router, prefix="/courses", tags=["Courses"])
app.include_router(activity_routes.router, prefix="/activities", tags=["Activities (Master Data)"])
app.include_router(tracking_routes.router, prefix="/logs", tags=["Interaction Logs (Start/Stop)"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

@app.get("/")
def root():
    return {"message": "API Ready. Documentation at /docs"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)