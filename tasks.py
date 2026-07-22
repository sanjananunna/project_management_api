from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.permissions import require_role

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


# ----------------------------------
# Create Task (Admin & Manager)
# ----------------------------------
@router.post("/", response_model=schemas.TaskResponse)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin", "Manager"]))
):

    project = db.query(models.Project).filter(
        models.Project.id == task.project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    user = db.query(models.User).filter(
        models.User.id == task.assigned_to
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Assigned user not found"
        )

    db_task = models.Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
        assigned_to=task.assigned_to,
        project_id=task.project_id
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


# ----------------------------------
# View All Tasks
# ----------------------------------
@router.get("/", response_model=list[schemas.TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin", "Manager", "Member"]))
):

    return db.query(models.Task).all()


# ----------------------------------
# View Task By ID
# ----------------------------------
@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin", "Manager", "Member"]))
):

    task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task
# ----------------------------------
# Update Task (Admin, Manager, Member)
# ----------------------------------
@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin", "Manager", "Member"]))
):

    task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # Members can update only their own assigned tasks
    if current_user.role == "Member" and task.assigned_to != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can update only your assigned tasks"
        )

    update_data = task_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    return task


# ----------------------------------
# Delete Task (Admin only)
# ----------------------------------
@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin"]))
):

    task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully"
    }