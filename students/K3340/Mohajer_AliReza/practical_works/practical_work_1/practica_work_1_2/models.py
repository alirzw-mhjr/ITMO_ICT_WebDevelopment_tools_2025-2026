from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from enums import BookCondition, ExchangeStatus


# ========== СВЯЗЬ МНОГИЕ-КО-МНОГИМ (книги <-> жанры) ==========
# Простая ассоциативная таблица без дополнительных полей
class BookGenreLink(SQLModel, table=True):
    __tablename__ = "book_genres"

    book_id: int = Field(foreign_key="books.id", primary_key=True)
    genre_id: int = Field(foreign_key="genres.id", primary_key=True)


# ========== СВЯЗЬ МНОГИЕ-КО-МНОГИМ (пользователи <-> книги) ==========
# Ассоциативная сущность с дополнительными полями
class UserBook(SQLModel, table=True):
    __tablename__ = "user_books"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    book_id: int = Field(foreign_key="books.id")
    condition: BookCondition = Field(default=BookCondition.GOOD)  # Enum
    is_available_for_swap: bool = Field(default=True)
    added_at: datetime = Field(default_factory=datetime.now)

    # Связи
    owner: "User" = Relationship(back_populates="user_books")
    book: "Book" = Relationship(back_populates="user_copies")


# ========== ПОЛЬЗОВАТЕЛЬ ==========
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True, index=True)
    display_name: str = Field(max_length=100)
    email: str = Field(max_length=100, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    location: Optional[str] = Field(max_length=100)
    preferences: str = Field(default="{}", max_length=500)
    created_at: datetime = Field(default_factory=datetime.now)
    bio: str = Field(default="", max_length=500)
    total_swaps: int = Field(default=0)
    is_active: bool = Field(default=True)

    # Связь с книгами пользователя
    user_books: List[UserBook] = Relationship(back_populates="owner")


# ========== КНИГА ==========
class Book(SQLModel, table=True):
    __tablename__ = "books"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, index=True)
    authors: str = Field(max_length=300)
    isbn: Optional[str] = Field(max_length=20, unique=True)
    description: str = Field(default="")
    published_year: Optional[int] = None
    page_count: Optional[int] = None

    # СВЯЗЬ МНОГИЕ-КО-МНОГИМ с жанрами (через простую таблицу)
    genres: List["Genre"] = Relationship(
        link_model=BookGenreLink,
        back_populates="books",
        sa_relationship_kwargs={"lazy": "selectin"},  # подгружать жанры сразу
    )

    # Связь с экземплярами книг пользователей
    user_copies: List[UserBook] = Relationship(back_populates="book")


# ========== ЖАНР ==========
class Genre(SQLModel, table=True):
    __tablename__ = "genres"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, unique=True, index=True)

    # Обратная связь многие-ко-многим с книгами
    books: List[Book] = Relationship(
        link_model=BookGenreLink,
        back_populates="genres",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
