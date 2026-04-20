from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from contextlib import asynccontextmanager

import database
import models
import schemas


# Запуск и остановка приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    # При старте - создаем таблицы
    database.init_db()
    yield
    # При остановке - ничего не делаем


app = FastAPI(
    title="BookCrossing API",
    description="Система обмена книгами с many-to-many связями",
    version="2.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {"message": "Welcome to BookCrossing API!"}


# ========== 1. ЭНДПОЙНТЫ ДЛЯ ЖАНРОВ ==========
@app.post("/genres", response_model=schemas.GenreRead, status_code=201)
def create_genre(
    genre_data: schemas.GenreCreate, session: Session = Depends(database.get_session)
):
    """Создать новый жанр"""
    existing = session.exec(
        select(models.Genre).where(models.Genre.name == genre_data.name)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Жанр уже существует")

    new_genre = models.Genre(name=genre_data.name)
    session.add(new_genre)
    session.commit()
    session.refresh(new_genre)
    return new_genre


@app.get("/genres", response_model=List[schemas.GenreRead])
def get_all_genres(session: Session = Depends(database.get_session)):
    """Получить все жанры"""
    return session.exec(select(models.Genre)).all()


# ========== 2. ЭНДПОЙНТЫ ДЛЯ КНИГ (С MANY-TO-MANY ЖАНРАМИ) ==========
@app.post("/books", response_model=schemas.BookRead, status_code=201)
def create_book(
    book_data: schemas.BookCreate, session: Session = Depends(database.get_session)
):
    """Создать книгу и привязать к жанрам (many-to-many)"""
    # Создаем книгу
    new_book = models.Book(
        title=book_data.title,
        authors=book_data.authors,
        isbn=book_data.isbn,
        description=book_data.description,
        published_year=book_data.published_year,
        page_count=book_data.page_count,
    )
    session.add(new_book)
    session.commit()

    # Привязываем жанры (many-to-many)
    if book_data.genre_ids:
        for genre_id in book_data.genre_ids:
            genre = session.get(models.Genre, genre_id)
            if genre:
                new_book.genres.append(genre)
        session.commit()

    session.refresh(new_book)
    return new_book


@app.get("/books", response_model=List[schemas.BookRead])
def get_all_books(session: Session = Depends(database.get_session)):
    """Получить все книги (с вложенными жанрами many-to-many)"""
    return session.exec(select(models.Book)).all()


@app.get("/books/{book_id}", response_model=schemas.BookRead)
def get_book(book_id: int, session: Session = Depends(database.get_session)):
    """Получить книгу по ID с ее жанрами (вложенный many-to-many)"""
    book = session.get(models.Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return book


@app.put("/books/{book_id}/genres", response_model=schemas.BookRead)
def update_book_genres(
    book_id: int, genre_ids: List[int], session: Session = Depends(database.get_session)
):
    """Обновить список жанров книги (many-to-many)"""
    book = session.get(models.Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    # Очищаем старые связи
    book.genres.clear()

    # Добавляем новые
    for genre_id in genre_ids:
        genre = session.get(models.Genre, genre_id)
        if genre:
            book.genres.append(genre)

    session.commit()
    session.refresh(book)
    return book


# ========== 3. ЭНДПОЙНТЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ==========
@app.post("/users", response_model=schemas.UserRead, status_code=201)
def create_user(
    user_data: schemas.UserCreate, session: Session = Depends(database.get_session)
):
    """Создать нового пользователя"""
    # Проверка уникальности
    if session.exec(
        select(models.User).where(models.User.username == user_data.username)
    ).first():
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
    if session.exec(
        select(models.User).where(models.User.email == user_data.email)
    ).first():
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    # TODO: хэшировать пароль
    new_user = models.User(
        username=user_data.username,
        display_name=user_data.display_name,
        email=user_data.email,
        password_hash=f"fake_hash_{user_data.password}",
        location=user_data.location,
        bio=user_data.bio,
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@app.get("/users", response_model=List[schemas.UserRead])
def get_all_users(session: Session = Depends(database.get_session)):
    """Получить всех пользователей (с их книгами)"""
    return session.exec(select(models.User)).all()


@app.get("/users/{user_id}", response_model=schemas.UserRead)
def get_user(user_id: int, session: Session = Depends(database.get_session)):
    """Получить пользователя по ID (с его книгами)"""
    user = session.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


# ========== 4. ЭНДПОЙНТЫ ДЛЯ ЭКЗЕМПЛЯРОВ КНИГ ПОЛЬЗОВАТЕЛЯ ==========
@app.post(
    "/users/{user_id}/books", response_model=schemas.UserBookRead, status_code=201
)
def add_book_to_user(
    user_id: int,
    userbook_data: schemas.UserBookCreate,
    session: Session = Depends(database.get_session),
):
    """Добавить экземпляр книги пользователю (с указанием состояния)"""
    user = session.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    book = session.get(models.Book, userbook_data.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена в каталоге")

    new_userbook = models.UserBook(
        user_id=user_id,
        book_id=userbook_data.book_id,
        condition=userbook_data.condition,
        is_available_for_swap=userbook_data.is_available_for_swap,
    )
    session.add(new_userbook)
    session.commit()
    session.refresh(new_userbook)
    return new_userbook


@app.get("/users/{user_id}/books", response_model=List[schemas.UserBookRead])
def get_user_books(user_id: int, session: Session = Depends(database.get_session)):
    """Получить все книги пользователя (с полной информацией о книгах)"""
    user = session.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user.user_books
