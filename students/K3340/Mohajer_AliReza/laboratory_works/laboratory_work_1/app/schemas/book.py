from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.genre import GenreOut


class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    authors: str | None = None
    isbn: str | None = Field(default=None, max_length=20)
    description: str | None = None
    published_year: int | None = None
    page_count: int | None = None


class BookCreate(BookBase):
    genre_ids: list[int] = Field(default_factory=list)


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    authors: str | None = None
    isbn: str | None = Field(default=None, max_length=20)
    description: str | None = None
    published_year: int | None = None
    page_count: int | None = None
    genre_ids: list[int] | None = None


class BookOut(BookBase):
    id: int
    genres: list[GenreOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class UserBookBase(BaseModel):
    condition: str | None = None
    status: str = "available"


class UserBookCreate(UserBookBase):
    book_id: int


class UserBookUpdate(BaseModel):
    condition: str | None = Field(default=None, max_length=50)
    status: str | None = Field(default=None, max_length=50)


class UserBookOut(UserBookBase):
    id: int
    user_id: int
    added_at: datetime
    book: BookOut

    model_config = {"from_attributes": True}
