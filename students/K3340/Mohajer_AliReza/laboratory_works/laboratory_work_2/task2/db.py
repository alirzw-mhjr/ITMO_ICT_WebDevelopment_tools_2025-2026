"""Общий модуль работы с базой данных для задачи 2.

Подключается к той же базе SQLite, что и лабораторная работа 1
(`laboratory_work_1/app.db`), и пишет результаты парсинга в таблицу `books`.
Используется всеми тремя вариантами парсера (threading, multiprocessing, async),
чтобы логика сохранения была одинаковой и сравнивались именно подходы к
параллельности, а не способ записи в БД.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

# Путь к базе данных из лабораторной работы 1 (../../laboratory_work_1/app.db).
DB_PATH = (
    Path(__file__).resolve().parents[2] / "laboratory_work_1" / "app.db"
)
DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

# check_same_thread=False — разрешаем работу из разных потоков (threading).
# timeout=30 — ждём снятия блокировки SQLite при одновременной записи из
# нескольких потоков/процессов, а не падаем сразу с "database is locked".
engine = create_engine(
    DATABASE_URL,
    future=True,
    connect_args={"check_same_thread": False, "timeout": 30},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, future=True)


class Base(DeclarativeBase):
    pass


class Book(Base):
    """Минимальное отображение существующей таблицы `books` из ЛР 1."""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    authors: Mapped[str | None] = mapped_column(Text, nullable=True)
    isbn: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)


def init_db() -> None:
    """Создаёт таблицу `books`, если базы ещё нет (на случай запуска без ЛР 1)."""
    Base.metadata.create_all(engine)


def save_book(title: str, authors: str | None = None) -> bool:
    """Сохраняет книгу в БД. Возвращает True, если запись добавлена.

    Если книга с таким заголовком уже есть, повторно не добавляем —
    так программу можно запускать несколько раз без дублей в таблице.
    """
    with SessionLocal() as session:
        exists = session.scalar(select(Book).where(Book.title == title))
        if exists is not None:
            return False
        session.add(Book(title=title, authors=authors))
        session.commit()
        return True
