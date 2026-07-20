from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas
from app.oauth2 import create_access_token, get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# -----------------------------
# Signup
# -----------------------------
@router.post("/signup", response_model=schemas.UserResponse)
def signup(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = crud.get_user_by_email(db, user.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = crud.create_user(db, user)

    return new_user


# -----------------------------
# Login
# -----------------------------
@router.post("/login", response_model=schemas.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = crud.authenticate_user(
        db,
        user_credentials.username,
        user_credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={"sub": user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# -----------------------------
# Current Logged-in User
# -----------------------------
@router.get("/me", response_model=schemas.UserResponse)
def get_me(
    current_user=Depends(get_current_user)
):
    return current_user


# -----------------------------
# Test Route
# -----------------------------
@router.get("/")
def test_auth():
    return {
        "message": "Authentication Router Working"
    }