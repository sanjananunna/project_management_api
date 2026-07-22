from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, crud
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
    background_tasks: BackgroundTasks,
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

    # Activity Log
    background_tasks.add_task(
        crud.log_activity,
        db,
        current_user.id,
        "Project Created",
        "Project",
        db_project.id
    )

    # Audit Log
    background_tasks.add_task(
        crud.create_audit_log,
        db,
        "Project",
        db_project.id,
        "action",
        None,
        "CREATE",
        current_user.id
    )

    # Notification
    background_tasks.add_task(
        crud.create_notification,
        db,
        current_user.id,
        "Project Created",
        f"Project '{db_project.name}' created successfully."
    )

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
    background_tasks: BackgroundTasks,
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

    project_name = project.name

    db.delete(project)
    db.commit()

    # Activity Log
    background_tasks.add_task(
        crud.log_activity,
        db,
        current_user.id,
        "Project Deleted",
        "Project",
        project_id
    )

    # Audit Log
    background_tasks.add_task(
        crud.create_audit_log,
        db,
        "Project",
        project_id,
        "action",
        None,
        "DELETE",
        current_user.id
    )

    # Notification
    background_tasks.add_task(
        crud.create_notification,
        db,
        current_user.id,
        "Project Deleted",
        f"Project '{project_name}' deleted successfully."
    )

    return {
        "message": "Project deleted successfully"
    }