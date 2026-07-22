from fastapi import FastAPI

from app.database import Base, engine
from app import models
from app.routers import (
    auth,
    projects,
    members,
    tasks,
    notifications,
    activities,
    audit_logs,
)
# Create database tables
#Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Project Management API",
    description="Project Management API with Authentication and RBAC",
    version="1.0.0"
)

# Routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(members.router)
app.include_router(tasks.router)
app.include_router(notifications.router)
app.include_router(activities.router)
app.include_router(audit_logs.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Project Management API"
    }