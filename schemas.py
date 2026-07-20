from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# ==========================
# User Schemas
# ==========================

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str = "Member"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================
# Project Schemas
# ==========================

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================
# Project Member Schemas
# ==========================

class ProjectMemberCreate(BaseModel):
    project_id: int
    user_id: int


# ==========================
# Task Schemas
# ==========================

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "Medium"
    due_date: Optional[datetime] = None
    assigned_to: int
    project_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    due_date: Optional[datetime] = None
    assigned_to: int
    project_id: int

    class Config:
        from_attributes = True


# ==========================
# JWT Token Schemas
# ==========================

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None