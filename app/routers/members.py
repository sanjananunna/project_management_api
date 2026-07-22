from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, crud
from app.permissions import require_role

router = APIRouter(
    prefix="/members",
    tags=["Project Members"]
)


# ----------------------------------
# Add Member to Project (Admin only)
# ----------------------------------
@router.post("/")
def add_member(
    member: schemas.ProjectMemberCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin"]))
):

    project = db.query(models.Project).filter(
        models.Project.id == member.project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    user = db.query(models.User).filter(
        models.User.id == member.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    existing = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == member.project_id,
        models.ProjectMember.user_id == member.user_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User is already a member of this project"
        )

    project_member = models.ProjectMember(
        project_id=member.project_id,
        user_id=member.user_id
    )

    db.add(project_member)
    db.commit()
    db.refresh(project_member)

    # Notification
    background_tasks.add_task(
        crud.create_notification,
        db,
        user.id,
        "Added to Project",
        f"You have been added to project '{project.name}'."
    )

    # Activity Log
    background_tasks.add_task(
        crud.log_activity,
        db,
        current_user.id,
        "Member Added",
        "Project",
        project.id,
        f"Added {user.full_name} to project '{project.name}'"
    )

    # Audit Log
    background_tasks.add_task(
        crud.create_audit_log,
        db,
        "Project",
        project.id,
        "member_added",
        None,
        user.full_name,
        current_user.id
    )

    return {
        "message": "Member added successfully"
    }


# ----------------------------------
# View Members of a Project
# ----------------------------------
@router.get("/{project_id}")
def get_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin", "Manager"]))
):

    project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    members = (
        db.query(models.ProjectMember)
        .filter(models.ProjectMember.project_id == project_id)
        .all()
    )

    return members