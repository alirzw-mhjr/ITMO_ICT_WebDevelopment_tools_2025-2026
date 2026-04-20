from __future__ import annotations


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.models import Book, Genre
from app.schemas.book import BookCreate, BookOut, BookUpdate

router = APIRouter()


def _load_book(book_id: int, db: Session) -> Book | None:
    return db.scalar(
        select(Book).where(Book.id == book_id).options(selectinload(Book.genres)),
    )


def _sync_genres(book: Book, genre_ids: list[int], db: Session) -> None:
    genres = list(db.scalars(select(Genre).where(Genre.id.in_(genre_ids))).all())
    if len(genres) != len(set(genre_ids)):
        raise HTTPException(status_code=400, detail="One or more genres were not found")
    book.genres = genres


@router.get("", response_model=list[BookOut])
def list_books(db: Session = Depends(get_db)) -> list[Book]:
    return list(
        db.scalars(
            select(Book).options(selectinload(Book.genres)).order_by(Book.title)
        ).all(),
    )


@router.post("", response_model=BookOut, status_code=201)
def create_book(body: BookCreate, db: Session = Depends(get_db)) -> Book:
    if body.isbn:
        if db.scalar(select(Book).where(Book.isbn == body.isbn)):
            raise HTTPException(
                status_code=400, detail="Book with this ISBN already exists"
            )
    book = Book(
        title=body.title,
        authors=body.authors,
        isbn=body.isbn,
        description=body.description,
        published_year=body.published_year,
        page_count=body.page_count,
    )
    db.add(book)
    db.flush()
    if body.genre_ids:
        _sync_genres(book, body.genre_ids, db)
    db.commit()
    db.refresh(book)
    b = _load_book(book.id, db)
    assert b is not None
    return b


@router.get("/{book_id}", response_model=BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)) -> Book:
    book = _load_book(book_id, db)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.patch("/{book_id}", response_model=BookOut)
def update_book(book_id: int, body: BookUpdate, db: Session = Depends(get_db)) -> Book:
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    data = body.model_dump(exclude_unset=True)
    genre_ids = data.pop("genre_ids", None)
    if "isbn" in data and data["isbn"]:
        exists = db.scalar(
            select(Book).where(Book.isbn == data["isbn"], Book.id != book_id)
        )
        if exists:
            raise HTTPException(
                status_code=400, detail="Book with this ISBN already exists"
            )
    for k, v in data.items():
        setattr(book, k, v)
    if genre_ids is not None:
        _sync_genres(book, genre_ids, db)
    db.add(book)
    db.commit()
    b = _load_book(book_id, db)
    assert b is not None
    return b


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)) -> None:
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
