from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.permissions import require_role

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"]
)


# ----------------------------------
# View All Audit Logs
# ----------------------------------
@router.get("/", response_model=list[schemas.AuditLogResponse])
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin"]))
):

    return (
        db.query(models.AuditLog)
        .order_by(models.AuditLog.changed_at.desc())
        .all()
    )


# ----------------------------------
# View Audit Logs for Specific Entity
# ----------------------------------
@router.get("/{entity_type}/{entity_id}", response_model=list[schemas.AuditLogResponse])
def get_entity_audit_logs(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin"]))
):

    return (
        db.query(models.AuditLog)
        .filter(
            models.AuditLog.entity_type == entity_type,
            models.AuditLog.entity_id == entity_id
        )
        .order_by(models.AuditLog.changed_at.desc())
        .all()
    )