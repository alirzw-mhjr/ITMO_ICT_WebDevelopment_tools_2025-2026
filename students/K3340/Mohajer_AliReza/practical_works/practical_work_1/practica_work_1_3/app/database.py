# app/database.py
import os
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bookcrossing.db")

# Создаем движок
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Показывать SQL запросы
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)


def init_db():
    """Создает все таблицы в базе данных"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Генератор сессий для Dependency Injection"""
    with Session(engine) as session:
        yield session
