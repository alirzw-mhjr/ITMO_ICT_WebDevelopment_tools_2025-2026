# Операции с БД, общие для сервисов.

from sqlalchemy import func, select

from common.database import SessionLocal
from common.models import Book


def save_book(title: str, authors: str | None = None) -> dict:
    """Сохраняет книгу. Если книга с таким заголовком уже есть — не дублирует.
    Возвращает словарь с результатом: id книги и флаг created.
    """
    with SessionLocal() as session:
        existing = session.scalar(select(Book).where(Book.title == title))
        if existing is not None:
            return {"id": existing.id, "title": existing.title, "created": False}

        book = Book(title=title, authors=authors)
        session.add(book)
        session.commit()
        session.refresh(book)
        return {"id": book.id, "title": book.title, "created": True}


def count_books() -> int:
    """Количество книг в БД (используется периодической задачей)."""
    with SessionLocal() as session:
        return int(session.scalar(select(func.count(Book.id))) or 0)
