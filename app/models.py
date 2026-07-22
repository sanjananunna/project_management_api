from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


# =========================
# User Model
# =========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="Member")  # Admin, Manager, Member
    created_at = Column(DateTime, default=datetime.utcnow)

    created_projects = relationship("Project", back_populates="creator")
    assigned_tasks = relationship("Task", back_populates="assignee")

    notifications = relationship("Notification", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


# =========================
# Project Model
# =========================
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="created_projects")
    members = relationship(
        "ProjectMember",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
    )


# =========================
# Project Members
# =========================
class ProjectMember(Base):
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    project = relationship("Project", back_populates="members")
    user = relationship("User")


# =========================
# Task Model
# =========================
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)

    status = Column(String, default="Pending")
    priority = Column(String, default="Medium")

    due_date = Column(DateTime)

    assigned_to = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))

    assignee = relationship("User", back_populates="assigned_tasks")
    project = relationship("Project", back_populates="tasks")


# =========================
# =========================
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)

    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


# =========================
# Activity Log Model
# =========================
class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer)

    description = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="activity_logs")


# =========================
# Audit Log Model
# =========================
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)

    field_name = Column(String)
    old_value = Column(Text)
    new_value = Column(Text)

    changed_by = Column(Integer, ForeignKey("users.id"))

    changed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")