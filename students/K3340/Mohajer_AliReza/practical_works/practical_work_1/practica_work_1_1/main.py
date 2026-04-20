from fastapi import FastAPI, HTTPException
from typing import List
from datetime import datetime
import models  # импортируем наши модели

app = FastAPI(title="BookCrossing Simple API")

# ========== ВРЕМЕННАЯ БАЗА ДАННЫХ (2 записи) ==========
# Каждый пользователь имеет:
# 1. Одиночный вложенный объект -> last_exchange (последний обмен)
# 2. Список объектов -> user_books (книги пользователя)

users_db = [
    {
        "id": 1,
        "username": "anna_reader",
        "email": "anna@example.com",
        "location": "Москва",
        "created_at": datetime(2024, 1, 15),
        # Одиночный вложенный объект
        "last_exchange": {
            "book_title": "Мастер и Маргарита",
            "exchange_date": datetime(2024, 2, 10),
            "with_user": "peter_books",
        },
        # Список объектов
        "user_books": [
            {
                "id": 101,
                "title": "Мастер и Маргарита",
                "author": "Булгаков",
                "condition": "good",
            },
            {
                "id": 102,
                "title": "451 градус по Фаренгейту",
                "author": "Брэдбери",
                "condition": "new",
            },
        ],
    },
    {
        "id": 2,
        "username": "peter_books",
        "email": "peter@example.com",
        "location": "СПб",
        "created_at": datetime(2024, 2, 1),
        # Одиночный вложенный объект
        "last_exchange": {
            "book_title": "Солярис",
            "exchange_date": datetime(2024, 2, 15),
            "with_user": "anna_reader",
        },
        # Список объектов
        "user_books": [
            {"id": 201, "title": "Солярис", "author": "Лем", "condition": "used"}
        ],
    },
    {
        "id": 3,
        "username": "elena_fantasy",
        "email": "elena@example.com",
        "location": "Казань",
        "created_at": datetime(2024, 3, 1),
        # У этого пользователя нет последнего обмена
        "last_exchange": None,
        # Пустой список книг
        "user_books": [],
    },
]


# Вспомогательная функция для поиска пользователя
def find_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    return None


# 1. GET все пользователи
@app.get("/users", response_model=List[models.User])
def get_all_users():
    """Возвращает всех пользователей с их книгами и последним обменом"""
    return users_db


# 2. GET один пользователь по ID
@app.get("/users/{user_id}", response_model=models.User)
def get_user(user_id: int):
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


# 3. POST создать пользователя
@app.post("/users", response_model=models.User, status_code=201)
def create_user(user_data: models.UserCreate):
    # Генерируем новый ID
    new_id = max(u["id"] for u in users_db) + 1

    new_user = {
        "id": new_id,
        "username": user_data.username,
        "email": user_data.email,
        "location": user_data.location,
        "created_at": datetime.now(),
        "last_exchange": None,
        "user_books": [],
    }
    users_db.append(new_user)
    return new_user


# 4. PUT полностью обновить пользователя
@app.put("/users/{user_id}", response_model=models.User)
def update_user(user_id: int, user_data: models.UserCreate):
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Обновляем поля
    user["username"] = user_data.username
    user["email"] = user_data.email
    user["location"] = user_data.location
    # created_at, last_exchange, user_books не трогаем

    return user


# ========== 5. PATCH частично обновить пользователя ==========
@app.patch("/users/{user_id}", response_model=models.User)
def patch_user(user_id: int, user_update: models.UserUpdate):
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Обновляем только те поля, которые переданы
    if user_update.username is not None:
        user["username"] = user_update.username
    if user_update.email is not None:
        user["email"] = user_update.email
    if user_update.location is not None:
        user["location"] = user_update.location

    return user


# 6. DELETE удалить пользователя
@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    users_db.remove(user)
    return None  # 204 No Content


# 7. GET получить только книги пользователя
@app.get("/users/{user_id}/books", response_model=List[models.UserBook])
def get_user_books(user_id: int):
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user["user_books"]


# 8. POST добавить книгу пользователю
@app.post("/users/{user_id}/books", response_model=models.UserBook, status_code=201)
def add_book_to_user(user_id: int, book: models.UserBook):
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверяем, нет ли уже такой книги
    for existing_book in user["user_books"]:
        if existing_book["id"] == book.id:
            raise HTTPException(status_code=400, detail="Книга уже есть")

    user["user_books"].append(book.dict())
    return book
