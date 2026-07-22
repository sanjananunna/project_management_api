from sqlalchemy.orm import Session
from app import models
from app.security import hash_password, verify_password


# =====================================================
# USER CRUD
# =====================================================

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user):
    hashed_pw = hash_password(user.password)

    db_user = models.User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_pw,
        role=user.role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


# =====================================================
# NOTIFICATION CRUD
# =====================================================

def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str
):
    notification = models.Notification(
        user_id=user_id,
        title=title,
        message=message
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


def get_notifications(db: Session, user_id: int):
    return (
        db.query(models.Notification)
        .filter(models.Notification.user_id == user_id)
        .order_by(models.Notification.created_at.desc())
        .all()
    )


# =====================================================
# ACTIVITY LOG CRUD
# =====================================================

def log_activity(
    db: Session,
    user_id: int,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    description: str | None = None
):
    activity = models.ActivityLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    return activity


def get_activity_logs(db: Session):
    return (
        db.query(models.ActivityLog)
        .order_by(models.ActivityLog.created_at.desc())
        .all()
    )


def get_user_activity_logs(db: Session, user_id: int):
    return (
        db.query(models.ActivityLog)
        .filter(models.ActivityLog.user_id == user_id)
        .order_by(models.ActivityLog.created_at.desc())
        .all()
    )


def get_project_activity_logs(db: Session, project_id: int):
    return (
        db.query(models.ActivityLog)
        .filter(
            models.ActivityLog.entity_type == "Project",
            models.ActivityLog.entity_id == project_id
        )
        .order_by(models.ActivityLog.created_at.desc())
        .all()
    )
# =====================================================
# AUDIT LOG CRUD
# =====================================================

def create_audit_log(
    db: Session,
    entity_type: str,
    entity_id: int,
    field_name: str | None = None,
    old_value: str | None = None,
    new_value: str | None = None,
    changed_by: int | None = None
):
    audit = models.AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
        changed_by=changed_by
    )

    db.add(audit)
    db.commit()
    db.refresh(audit)

    return audit


def get_audit_logs(db: Session):
    return (
        db.query(models.AuditLog)
        .order_by(models.AuditLog.changed_at.desc())
        .all()
    )


def get_entity_audit_logs(
    db: Session,
    entity_type: str,
    entity_id: int
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