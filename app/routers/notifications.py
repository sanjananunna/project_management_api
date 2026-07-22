from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.permissions import require_role

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# ----------------------------------
# View My Notifications
# ----------------------------------
@router.get("/", response_model=list[schemas.NotificationResponse])
def get_notifications(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin", "Manager", "Member"]))
):
    return (
        db.query(models.Notification)
        .filter(models.Notification.user_id == current_user.id)
        .order_by(models.Notification.created_at.desc())
        .all()
    )


# ----------------------------------
# View Unread Notifications
# ----------------------------------
@router.get("/unread", response_model=list[schemas.NotificationResponse])
def get_unread_notifications(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin", "Manager", "Member"]))
):
    return (
        db.query(models.Notification)
        .filter(
            models.Notification.user_id == current_user.id,
            models.Notification.is_read == False
        )
        .order_by(models.Notification.created_at.desc())
        .all()
    )


# ----------------------------------
# Mark Notification as Read
# ----------------------------------
@router.put("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin", "Manager", "Member"]))
):

    notification = (
        db.query(models.Notification)
        .filter(
            models.Notification.id == notification_id,
            models.Notification.user_id == current_user.id
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    notification.is_read = True
    db.commit()

    return {"message": "Notification marked as read"}


# ----------------------------------
# Mark All Notifications as Read
# ----------------------------------
@router.put("/read-all")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin", "Manager", "Member"]))
):

    notifications = (
        db.query(models.Notification)
        .filter(models.Notification.user_id == current_user.id)
        .all()
    )

    for notification in notifications:
        notification.is_read = True

    db.commit()

    return {"message": "All notifications marked as read"}


# ----------------------------------
# Delete Notification
# ----------------------------------
@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Admin", "Manager", "Member"]))
):

    notification = (
        db.query(models.Notification)
        .filter(
            models.Notification.id == notification_id,
            models.Notification.user_id == current_user.id
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    db.delete(notification)
    db.commit()

    return {"message": "Notification deleted successfully"}