from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.models.book import Book
from app.models.genre import Genre
from app.models.user_book import UserBook
from app.models.book_genre import BookGenre
from app.schemas.book import UserBookCreate, UserBookOut, UserBookUpdate

router = APIRouter()

_ALLOWED_UB_STATUS = frozenset({"available", "swapped", "unavailable"})


def _ub_options():
    return selectinload(UserBook.book).selectinload(Book.genres)


@router.get("/mine", response_model=list[UserBookOut])
def my_library(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[UserBook]:
    return list(
        db.scalars(
            select(UserBook)
            .where(UserBook.user_id == current.id)
            .options(_ub_options())
            .order_by(UserBook.added_at.desc()),
        ).all(),
    )


@router.post("", response_model=UserBookOut, status_code=201)
def add_to_library(
    body: UserBookCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> UserBook:
    book = db.get(Book, body.book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    exists = db.scalar(
        select(UserBook).where(
            UserBook.user_id == current.id, UserBook.book_id == body.book_id
        ),
    )
    if exists:
        raise HTTPException(
            status_code=400, detail="This book is already in your library"
        )
    if body.status not in _ALLOWED_UB_STATUS:
        raise HTTPException(status_code=400, detail="Invalid status")
    ub = UserBook(
        user_id=current.id,
        book_id=body.book_id,
        condition=body.condition,
        status=body.status,
    )
    db.add(ub)
    db.commit()
    out = db.scalar(select(UserBook).where(UserBook.id == ub.id).options(_ub_options()))
    assert out is not None
    return out


@router.get("/{userbook_id}", response_model=UserBookOut)
def get_userbook(userbook_id: int, db: Session = Depends(get_db)) -> UserBook:
    ub = db.scalar(
        select(UserBook).where(UserBook.id == userbook_id).options(_ub_options())
    )
    if ub is None:
        raise HTTPException(status_code=404, detail="User book not found")
    return ub


@router.patch("/{userbook_id}", response_model=UserBookOut)
def update_userbook(
    userbook_id: int,
    body: UserBookUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> UserBook:
    ub = db.get(UserBook, userbook_id)
    if ub is None:
        raise HTTPException(status_code=404, detail="User book not found")
    if ub.user_id != current.id:
        raise HTTPException(status_code=403, detail="Not your library item")
    data = body.model_dump(exclude_unset=True)
    if "status" in data and data["status"] is not None:
        if data["status"] not in _ALLOWED_UB_STATUS:
            raise HTTPException(status_code=400, detail="Invalid status")
    for k, v in data.items():
        setattr(ub, k, v)
    db.add(ub)
    db.commit()
    out = db.scalar(select(UserBook).where(UserBook.id == ub.id).options(_ub_options()))
    assert out is not None
    return out


@router.delete("/{userbook_id}", status_code=204)
def remove_userbook(
    userbook_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> None:
    ub = db.get(UserBook, userbook_id)
    if ub is None:
        raise HTTPException(status_code=404, detail="User book not found")
    if ub.user_id != current.id:
        raise HTTPException(status_code=403, detail="Not your library item")
    db.delete(ub)
    db.commit()
