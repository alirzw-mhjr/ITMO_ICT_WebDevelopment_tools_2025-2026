# Подключение к базе данных (общее для всех сервисов).
# По умолчанию используется тот же SQLite, что и в лабораторной работе 1.

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# В контейнерах файл лаб 1 примонтирован в /lab1 (см. docker-compose.yml).
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////lab1/app.db")

_connect_args: dict = {}
if DATABASE_URL.startswith("sqlite"):
    # check_same_thread=False — доступ из разных потоков;
    # timeout=30 — ждать снятия блокировки SQLite, а не падать сразу.
    _connect_args = {"check_same_thread": False, "timeout": 30}

engine = create_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True,
    connect_args=_connect_args,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, future=True)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    # Импорт нужен, чтобы модель Book зарегистрировалась в метаданных Base.
    from common import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
