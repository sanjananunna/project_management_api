from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models, schemas
from app.permissions import require_role

router = APIRouter(
    prefix="/activities",
    tags=["Activities"]
)


# ----------------------------------
# View All Activities
# ----------------------------------
@router.get("/", response_model=list[schemas.ActivityLogResponse])
def get_activity_logs(
    action: str | None = Query(None),
    activity_date: date | None = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin", "Manager"]))
):

    query = db.query(models.ActivityLog)

    if action:
        query = query.filter(models.ActivityLog.action.ilike(f"%{action}%"))

    if activity_date:
        query = query.filter(
            func.date(models.ActivityLog.created_at) == activity_date
        )

    return query.order_by(models.ActivityLog.created_at.desc()).all()


# ----------------------------------
# View Activities of a User
# ----------------------------------
@router.get("/user/{user_id}", response_model=list[schemas.ActivityLogResponse])
def get_user_activities(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin", "Manager"]))
):

    return (
        db.query(models.ActivityLog)
        .filter(models.ActivityLog.user_id == user_id)
        .order_by(models.ActivityLog.created_at.desc())
        .all()
    )


# ----------------------------------
# View Activities of a Project
# ----------------------------------
@router.get("/project/{project_id}", response_model=list[schemas.ActivityLogResponse])
def get_project_activities(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin", "Manager"]))
):

    return (
        db.query(models.ActivityLog)
        .filter(
            models.ActivityLog.entity_type == "Project",
            models.ActivityLog.entity_id == project_id
        )
        .order_by(models.ActivityLog.created_at.desc())
        .all()
    )