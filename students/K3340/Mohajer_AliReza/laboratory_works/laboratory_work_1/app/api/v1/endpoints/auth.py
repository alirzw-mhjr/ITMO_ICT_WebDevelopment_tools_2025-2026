from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas.auth import LoginIn, TokenOut
from app.schemas.user import ChangePasswordIn, UserCreate, UserOut

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(body: UserCreate, db: Session = Depends(get_db)) -> User:
    if db.scalar(select(User).where(User.username == body.username)):
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.scalar(select(User).where(User.email == body.email)):
        raise HTTPException(status_code=400, detail="Email already registered")
    # print(f"Hashing password: {body.password}")
    # print(f"Hashed password: {hash_password(body.password)}")
    user = User(
        username=body.username,
        display_name=body.display_name,
        email=str(body.email),
        password_hash=hash_password(body.password),
        location=body.location,
        preferences=body.preferences,
        bio=body.bio,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    user = db.scalar(select(User).where(User.username == body.username))
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive"
        )
    token = create_access_token(user_id=user.id, username=user.username)
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)) -> User:
    print(f"Current user: {current}")
    return current


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    body: ChangePasswordIn,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> None:
    if not verify_password(body.old_password, current.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current.password_hash = hash_password(body.new_password)
    db.add(current)
    db.commit()
