from fastapi import FastAPI
import uvicorn

# Import Routes
from modules.students import routes as student_routes
from modules.courses import routes as course_routes
<<<<<<< HEAD
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
=======
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
>>>>>>> c20463b35a8d886f254c1a5445aa1b0b1e7056a1

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)