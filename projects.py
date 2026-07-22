from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.permissions import require_role

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


# ----------------------------------
# Create Project (Admin only)
# ----------------------------------
@router.post("/", response_model=schemas.ProjectResponse)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin"]))
):

    db_project = models.Project(
        name=project.name,
        description=project.description,
        created_by=current_user.id
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project


# ----------------------------------
# View All Projects
# ----------------------------------
@router.get("/", response_model=list[schemas.ProjectResponse])
def get_projects(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin", "Manager", "Member"]))
):

    return db.query(models.Project).all()


# ----------------------------------
# Get Project by ID
# ----------------------------------
@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin", "Manager", "Member"]))
):

    project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return project


# ----------------------------------
# Delete Project (Admin only)
# ----------------------------------
@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin"]))
):

    project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    db.delete(project)
    db.commit()

    return {
        "message": "Project deleted successfully"
    }