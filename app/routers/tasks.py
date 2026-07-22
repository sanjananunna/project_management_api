from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, crud
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
    background_tasks: BackgroundTasks,
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

    # Notification
    background_tasks.add_task(
        crud.create_notification,
        db,
        user.id,
        "Task Assigned",
        f"You have been assigned task '{db_task.title}'"
    )

    # Activity
    background_tasks.add_task(
        crud.log_activity,
        db,
        current_user.id,
        "Task Created",
        "Task",
        db_task.id,
        f"Created task '{db_task.title}'"
    )

    # Audit
    background_tasks.add_task(
        crud.create_audit_log,
        db,
        "Task",
        db_task.id,
        "created",
        None,
        db_task.title,
        current_user.id
    )

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
    background_tasks: BackgroundTasks,
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

    # Members can update only their assigned tasks
    if current_user.role == "Member" and task.assigned_to != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can update only your assigned tasks"
        )

    old_status = task.status

    update_data = task_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    # Activity Log
    background_tasks.add_task(
        crud.log_activity,
        db,
        current_user.id,
        "Task Updated",
        "Task",
        task.id,
        f"Updated task '{task.title}'"
    )

    # Audit Log
    background_tasks.add_task(
        crud.create_audit_log,
        db,
        "Task",
        task.id,
        "updated",
        old_status,
        task.status,
        current_user.id
    )

    # Notification when task is completed
    if task.status.lower() == "completed":
        background_tasks.add_task(
            crud.create_notification,
            db,
            task.assigned_to,
            "Task Completed",
            f"Task '{task.title}' has been marked as completed."
        )

    return task
# ----------------------------------
# Delete Task (Admin only)
# ----------------------------------
@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    background_tasks: BackgroundTasks,
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

    task_title = task.title
    task_id_value = task.id
    assigned_user = task.assigned_to

    db.delete(task)
    db.commit()

    # Notification
    background_tasks.add_task(
        crud.create_notification,
        db,
        assigned_user,
        "Task Deleted",
        f"Task '{task_title}' has been deleted."
    )

    # Activity Log
    background_tasks.add_task(
        crud.log_activity,
        db,
        current_user.id,
        "Task Deleted",
        "Task",
        task_id_value,
        f"Deleted task '{task_title}'"
    )

    # Audit Log
    background_tasks.add_task(
        crud.create_audit_log,
        db,
        "Task",
        task_id_value,
        "deleted",
        task_title,
        None,
        current_user.id
    )

    return {
        "message": "Task deleted successfully"
    }