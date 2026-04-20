from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from enums import BookCondition, ExchangeStatus


# ========== СХЕМЫ ДЛЯ ЖАНРОВ ==========
class GenreBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class GenreCreate(GenreBase):
    pass


class GenreRead(GenreBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ========== СХЕМЫ ДЛЯ КНИГ (С ВЛОЖЕННЫМИ ЖАНРАМИ) ==========
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    authors: str = Field(..., min_length=1, max_length=300)
    isbn: Optional[str] = Field(None, max_length=20)
    description: str = ""
    published_year: Optional[int] = Field(None, ge=0, le=datetime.now().year)
    page_count: Optional[int] = Field(None, ge=1)


class BookCreate(BookBase):
    genre_ids: Optional[List[int]] = []  # ID жанров для связи


class BookRead(BookBase):
    id: int
    genres: List[GenreRead] = []  # ← ВЛОЖЕННЫЙ СПИСОК (many-to-many)
    model_config = ConfigDict(from_attributes=True)


# ========== СХЕМЫ ДЛЯ ЭКЗЕМПЛЯРОВ КНИГ ПОЛЬЗОВАТЕЛЯ ==========
class UserBookBase(BaseModel):
    condition: BookCondition = BookCondition.GOOD
    is_available_for_swap: bool = True


class UserBookCreate(UserBookBase):
    book_id: int


class UserBookRead(UserBookBase):
    id: int
    user_id: int
    book_id: int
    added_at: datetime
    book: BookRead  # ← ВЛОЖЕННЫЙ ОБЪЕКТ (книга целиком)
    model_config = ConfigDict(from_attributes=True)


# ========== СХЕМЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ (С ВЛОЖЕННЫМИ КНИГАМИ) ==========
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^\S+@\S+\.\S+$")
    location: Optional[str] = None
    bio: str = ""


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserRead(UserBase):
    id: int
    created_at: datetime
    total_swaps: int
    is_active: bool
    user_books: List[UserBookRead] = []  # ← ВЛОЖЕННЫЙ СПИСОК
    model_config = ConfigDict(from_attributes=True)
