from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Genre
from app.schemas.genre import GenreCreate, GenreOut, GenreUpdate

router = APIRouter()


@router.get("", response_model=list[GenreOut])
def list_genres(db: Session = Depends(get_db)) -> list[Genre]:
    return list(db.scalars(select(Genre).order_by(Genre.name)).all())


@router.post("", response_model=GenreOut, status_code=201)
def create_genre(body: GenreCreate, db: Session = Depends(get_db)) -> Genre:
    if db.scalar(select(Genre).where(Genre.name == body.name)):
        raise HTTPException(status_code=400, detail="Genre already exists")
    g = Genre(name=body.name)
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


@router.get("/{genre_id}", response_model=GenreOut)
def get_genre(genre_id: int, db: Session = Depends(get_db)) -> Genre:
    g = db.get(Genre, genre_id)
    if g is None:
        raise HTTPException(status_code=404, detail="Genre not found")
    return g


@router.patch("/{genre_id}", response_model=GenreOut)
def update_genre(
    genre_id: int, body: GenreUpdate, db: Session = Depends(get_db)
) -> Genre:
    g = db.get(Genre, genre_id)
    if g is None:
        raise HTTPException(status_code=404, detail="Genre not found")
    if body.name is not None:
        if db.scalar(
            select(Genre).where(Genre.name == body.name, Genre.id != genre_id)
        ):
            raise HTTPException(status_code=400, detail="Genre name already taken")
        g.name = body.name
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


@router.delete("/{genre_id}", status_code=204)
def delete_genre(genre_id: int, db: Session = Depends(get_db)) -> None:
    g = db.get(Genre, genre_id)
    if g is None:
        raise HTTPException(status_code=404, detail="Genre not found")
    db.delete(g)
    db.commit()
