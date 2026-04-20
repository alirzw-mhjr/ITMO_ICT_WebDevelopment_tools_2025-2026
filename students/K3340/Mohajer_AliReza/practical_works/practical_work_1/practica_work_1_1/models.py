# models.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# Модель для одиночного вложенного объекта (последний обмен)
class LastExchange(BaseModel):
    book_title: str
    exchange_date: datetime
    with_user: str


# Модель для списка объектов (книги пользователя)
class UserBook(BaseModel):
    id: int
    title: str
    author: str
    condition: str  # new, good, used, damaged


# ГЛАВНАЯ МОДЕЛЬ (пользователь) с вложенными объектами
class User(BaseModel):
    id: int
    username: str
    email: str
    location: str
    created_at: datetime
    last_exchange: Optional[LastExchange] = None  # одиночный вложенный
    user_books: List[UserBook] = []  # список объектов


# Модель для создания нового пользователя (без id и даты)
class UserCreate(BaseModel):
    username: str
    email: str
    location: str


# Модель для обновления пользователя
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
