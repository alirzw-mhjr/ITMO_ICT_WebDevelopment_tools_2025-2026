from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.book import Book
from app.models.user_book import UserBook
from app.models import User
from app.schemas.user import UserDetailOut, UserOut, UserUpdate

router = APIRouter()


@router.get("", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    active_only: bool = Query(default=True),
) -> list[User]:
    q = select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
    if active_only:
        q = q.where(User.is_active.is_(True))
    return list(db.scalars(q).all())


@router.patch("/me", response_model=UserOut)
def update_my_profile(
    body: UserUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> User:
    print(f"Updating profile for user: {current.id}")
    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(current, k, v)
    db.add(current)
    db.commit()
    db.refresh(current)
    return current


@router.get("/{user_id}", response_model=UserDetailOut)
def get_user(user_id: int, db: Session = Depends(get_db)) -> User:
    user = db.scalar(
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.userbooks)
            .selectinload(UserBook.book)
            .selectinload(Book.genres),
        ),
    )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
