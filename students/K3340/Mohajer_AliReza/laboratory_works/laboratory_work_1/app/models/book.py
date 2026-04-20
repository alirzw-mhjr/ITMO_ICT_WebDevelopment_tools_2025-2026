from __future__ import annotations

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    authors: Mapped[str | None] = mapped_column(Text, nullable=True)
    isbn: Mapped[str | None] = mapped_column(
        String(20), unique=True, nullable=True, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    userbooks: Mapped[list["UserBook"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )
    genres: Mapped[list["Genre"]] = relationship(
        secondary="book_genres",
        back_populates="books",
    )
