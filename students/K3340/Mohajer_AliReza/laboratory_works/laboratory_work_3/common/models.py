# Модель Book — точно повторяет таблицу books из лабораторной работы 1,
# чтобы запись шла в ту же базу SQLite без изменения её схемы.

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from common.database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    authors: Mapped[str | None] = mapped_column(Text, nullable=True)
    isbn: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
