from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

# Для SQLite (разработка)
DATABASE_URL = "sqlite:///./bookcrossing.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,  # показывать SQL-запросы в консоли
    connect_args={"check_same_thread": False},  # только для SQLite
)


def init_db():
    """Создает все таблицы в базе данных"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Генератор сессий для Dependency Injection"""
    with Session(engine) as session:
        yield session
