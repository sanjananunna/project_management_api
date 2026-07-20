from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
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

    members = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id
    ).all()

    return members