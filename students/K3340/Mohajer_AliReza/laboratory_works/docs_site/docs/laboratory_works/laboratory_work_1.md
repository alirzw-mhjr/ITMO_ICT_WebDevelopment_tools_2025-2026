# Лабораторная работа 1

Выполнены:

- практическая работа 1.1 — базовое FastAPI-приложение с временными данными;
- практическая работа 1.2 — перенос приложения на SQLAlchemy и Pydantic, реализация таблиц и связей;
- практическая работа 1.3 — настройка Alembic и миграций базы данных.
- модели данных в соответствии с предметной областью;
- авторизация и JWT;

---

## Тема

Реализация серверного приложения FastAPI по предметной области буккроссинга.

## Цель работы

Разработать серверное приложение на FastAPI с использованием SQLAlchemy, Pydantic, Alembic и механизмов аутентификации, реализующее предметную область сервиса для обмена книгами между пользователями.

## Выбранная тема

Разработка веб-приложения для буккроссинга.

Приложение позволяет пользователям:

- **регистрироваться и входить** в систему с использованием JWT;
- **создавать и редактировать профиль** с дополнительной информацией (локация, биография, предпочтения);
- **добавлять книги** в личную библиотеку с указанием состояния (новая, хорошее, приемлемое, плохое);
- **отправлять и принимать запросы** на обмен книгами;
- **отправлять сообщения** в рамках конкретного обмена;
- **управлять статусами обменов** (ожидание, принято, отклонено, завершено, отменено);
- **просматривать историю** своих обменов и статистику.

---

## Архитектура и модель данных

### Таблицы базы данных

Приложение использует следующую структуру БД:

#### 1. Таблица `Users`

Основная информация о пользователях системы.

| Поле          | Тип          | Описание                             |
| ------------- | ------------ | ------------------------------------ |
| id            | INTEGER      | Уникальный идентификатор (PK)        |
| username      | VARCHAR(50)  | Уникальное имя пользователя          |
| display_name  | VARCHAR(100) | Отображаемое имя (опционально)       |
| email         | VARCHAR(255) | Уникальный email                     |
| password_hash | VARCHAR(255) | Хеш пароля                           |
| location      | VARCHAR(100) | Локация пользователя (опционально)   |
| preferences   | TEXT         | Предпочтения по книгам (опционально) |
| bio           | TEXT         | Биография (опционально)              |
| created_at    | TIMESTAMP    | Дата регистрации                     |
| total_swaps   | INTEGER      | Количество завершенных обменов       |
| is_active     | BOOLEAN      | Статус активности пользователя       |

#### 2. Таблица `Books`

Каталог всех книг в системе.

| Поле           | Тип          | Описание                       |
| -------------- | ------------ | ------------------------------ |
| id             | INTEGER      | Уникальный идентификатор (PK)  |
| title          | VARCHAR(255) | Название книги                 |
| authors        | TEXT         | Авторы книги                   |
| ISBN           | VARCHAR(20)  | ISBN (опционально, уникальный) |
| description    | TEXT         | Описание книги                 |
| published_year | INTEGER      | Год публикации                 |
| page_count     | INTEGER      | Количество страниц             |

#### 3. Таблица `UserBooks`

Связь пользователя с его книгами (что и в каком состоянии есть у каждого пользователя).

| Поле      | Тип         | Описание                                |
| --------- | ----------- | --------------------------------------- |
| id        | INTEGER     | Уникальный идентификатор (PK)           |
| user_id   | INTEGER     | ID пользователя (FK)                    |
| book_id   | INTEGER     | ID книги (FK)                           |
| condition | VARCHAR(50) | Состояние: new, good, acceptable, poor  |
| status    | VARCHAR(50) | Статус: available, swapped, unavailable |
| added_at  | TIMESTAMP   | Дата добавления в библиотеку            |

**Ограничения:**

- UNIQUE(user_id, book_id) — пользователь не может иметь дублирующиеся копии одной книги

#### 4. Таблица `Genres`

Жанры/категории книг.

| Поле | Тип          | Описание                      |
| ---- | ------------ | ----------------------------- |
| id   | INTEGER      | Уникальный идентификатор (PK) |
| name | VARCHAR(100) | Название жанра (уникальное)   |

#### 5. Таблица `BookGenres`

Связь many-to-many между книгами и жанрами.

| Поле     | Тип     | Описание                      |
| -------- | ------- | ----------------------------- |
| id       | INTEGER | Уникальный идентификатор (PK) |
| book_id  | INTEGER | ID книги (FK)                 |
| genre_id | INTEGER | ID жанра (FK)                 |

**Ограничения:**

- UNIQUE(book_id, genre_id) — книга не может иметь один жанр дважды

#### 6. Таблица `Exchanges`

Запросы на обмен между пользователями.

| Поле                  | Тип         | Описание                                                  |
| --------------------- | ----------- | --------------------------------------------------------- |
| id                    | INTEGER     | Уникальный идентификатор (PK)                             |
| requester_id          | INTEGER     | ID пользователя, который запросил обмен (FK)              |
| owner_id              | INTEGER     | ID пользователя-владельца запрашиваемой книги (FK)        |
| requested_userbook_id | INTEGER     | ID UserBooks книги, которую запрашивает пользователь (FK) |
| offered_userbook_id   | INTEGER     | ID UserBooks книги, которую предлагает пользователь (FK)  |
| message               | TEXT        | Сообщение к запросу (опционально)                         |
| status                | VARCHAR(50) | Статус: pending, accepted, rejected, completed, cancelled |
| requested_at          | TIMESTAMP   | Дата создания запроса                                     |
| exchange_at           | TIMESTAMP   | Дата завершения обмена (опционально)                      |

#### 7. Таблица `Messages`

Сообщения в рамках конкретного обмена.

| Поле         | Тип       | Описание                      |
| ------------ | --------- | ----------------------------- |
| id           | INTEGER   | Уникальный идентификатор (PK) |
| exchange_id  | INTEGER   | ID обмена (FK)                |
| sender_id    | INTEGER   | ID отправителя (FK)           |
| receiver_id  | INTEGER   | ID получателя (FK)            |
| message_text | TEXT      | Текст сообщения               |
| is_read      | BOOLEAN   | Прочитано ли сообщение        |
| sent_at      | TIMESTAMP | Дата отправки                 |

### Диаграмма связей

```
Users
  ├── 1 ---> * UserBooks
  ├── 1 ---> * Exchanges (как requester_id)
  ├── 1 ---> * Exchanges (как owner_id)
  └── 1 ---> * Messages (как sender_id и receiver_id)

Books
  ├── 1 ---> * UserBooks
  ├── 1 ---> * BookGenres
  └── 1 ---> * Exchanges (через UserBooks)

Genres
  └── 1 ---> * BookGenres

UserBooks
  ├── * ---> * Exchanges (requested_userbook_id, offered_userbook_id)
  └── * ---> * Exchanges

Exchanges
  └── 1 ---> * Messages

Messages
  └── * (связь с Users)
```

---

## Выполненные практические работы

### Практическая работа 1.1

На первом этапе было создано базовое приложение FastAPI с временными данными.

Были реализованы:

- endpoint для book;
- endpoint для user;
- базовая работа со Swagger;
- использование Pydantic-моделей для валидации данных.

### Практическая работа 1.2

На втором этапе приложение было переведено на PostgreSQL и SQLModel.

Были реализованы таблицы:

- `User` — информация о пользователях;
- `Book` — книги в системе;
- `UserBook` — связь между пользователями и книгами
- `Genre` — жанры книг;
- `BookGenreLink` — связь между книгами и жанрами.

### Практическая работа 1.3

На третьем этапе была подключена система миграций Alembic.

Были выполнены:

- инициализация Alembic;
- настройка `alembic.ini`;
- настройка `migrations/env.py`;
- создание и применение миграций;
- перевод проекта на управление схемой базы данных через Alembic.

---

## Реализованные API эндпоинты

### Аутентификация (`/api/v1/auth/`)

#### Регистрация

```
POST /api/v1/auth/register
```

**Описание:** Регистрация нового пользователя  
**Статус ответа:** 201 (Created)  
**Тело запроса:**

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword",
  "display_name": "John Doe",
  "location": "New York",
  "preferences": "Science fiction, Fantasy",
  "bio": "Book lover since 2010"
}
```

**Ответ:**

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-04-21T10:30:00",
  "total_swaps": 0,
  "is_active": true
}
```

#### Вход в систему

```
POST /api/v1/auth/login
```

**Описание:** Вход с получением JWT токена  
**Статус ответа:** 200 (OK)  
**Тело запроса:**

```json
{
  "username": "john_doe",
  "password": "securepassword"
}
```

**Ответ:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Получить информацию о текущем пользователе

```
GET /api/v1/auth/me
```

**Требуется:** Bearer токен  
**Статус ответа:** 200 (OK)  
**Ответ:** UserOut (см. выше)

#### Изменить пароль

```
POST /api/v1/auth/change-password
```

**Требуется:** Bearer токен  
**Статус ответа:** 204 (No Content)  
**Тело запроса:**

```json
{
  "old_password": "oldpassword",
  "new_password": "newpassword"
}
```

### Пользователи (`/api/v1/users/`)

#### Получить список пользователей

```
GET /api/v1/users/?skip=0&limit=50&active_only=true
```

**Параметры:**

- `skip`: пропустить N записей (по умолчанию 0)
- `limit`: вернуть N записей (по умолчанию 50, максимум 200)
- `active_only`: показать только активных пользователей (по умолчанию true)

**Ответ:**

```json
[
  {
    "id": 1,
    "username": "john_doe",
    "display_name": "John Doe",
    "email": "john@example.com",
    "location": "New York",
    "created_at": "2024-04-21T10:30:00",
    "bio": "Book lover",
    "total_swaps": 5,
    "is_active": true
  }
]
```

#### Получить детальную информацию о пользователе

```
GET /api/v1/users/{user_id}
```

**Ответ:**

```json
{
  "id": 1,
  "username": "john_doe",
  "display_name": "John Doe",
  "email": "john@example.com",
  "location": "New York",
  "created_at": "2024-04-21T10:30:00",
  "bio": "Book lover",
  "total_swaps": 5,
  "is_active": true,
  "userbooks": [
    {
      "id": "uuid-123",
      "book_id": "uuid-book-1",
      "condition": "good",
      "status": "available",
      "added_at": "2024-04-20T15:00:00",
      "book": {
        "id": "uuid-book-1",
        "title": "Dune",
        "authors": "Frank Herbert",
        "description": "Epic science fiction",
        "genres": [...]
      }
    }
  ]
}
```

#### Обновить свой профиль

```
PATCH /api/v1/users/me
```

**Требуется:** Bearer токен  
**Статус ответа:** 200 (OK)  
**Тело запроса:**

```json
{
  "display_name": "John D.",
  "location": "Boston",
  "preferences": "Science fiction",
  "bio": "Updated bio"
}
```

### Жанры (`/api/v1/genres/`)

#### Получить все жанры

```
GET /api/v1/genres/
```

**Ответ:**

```json
[
  {
    "id": "uuid-1",
    "name": "Science Fiction"
  },
  {
    "id": "uuid-2",
    "name": "Fantasy"
  }
]
```

#### Создать новый жанр

```
POST /api/v1/genres/
```

**Требуется:** Bearer токен  
**Статус ответа:** 201 (Created)  
**Тело запроса:**

```json
{
  "name": "Mystery"
}
```

### Книги (`/api/v1/books/`)

#### Получить все книги

```
GET /api/v1/books/?skip=0&limit=50
```

**Параметры:**

- `skip`: пропустить N записей
- `limit`: вернуть N записей

**Ответ:**

```json
[
  {
    "id": "uuid-book-1",
    "title": "Dune",
    "authors": "Frank Herbert",
    "ISBN": "0-441-13959-0",
    "description": "A epic science fiction novel",
    "published_year": 1965,
    "page_count": 680,
    "genres": [
      {
        "id": "uuid-1",
        "name": "Science Fiction"
      }
    ]
  }
]
```

#### Получить книгу по ID

```
GET /api/v1/books/{book_id}
```

#### Создать новую книгу

```
POST /api/v1/books/
```

**Требуется:** Bearer токен  
**Статус ответа:** 201 (Created)  
**Тело запроса:**

```json
{
  "title": "The Foundation",
  "authors": "Isaac Asimov",
  "ISBN": "0-553-29438-0",
  "description": "Foundation series",
  "published_year": 1951,
  "page_count": 255,
  "genre_ids": ["uuid-1"]
}
```

#### Обновить книгу

```
PATCH /api/v1/books/{book_id}
```

**Требуется:** Bearer токен  
**Статус ответа:** 200 (OK)

#### Удалить книгу

```
DELETE /api/v1/books/{book_id}
```

**Требуется:** Bearer токен  
**Статус ответа:** 204 (No Content)

### Библиотека пользователя (`/api/v1/user-books/`)

#### Получить все книги пользователя

```
GET /api/v1/user-books/?skip=0&limit=50
```

#### Добавить книгу в библиотеку

```
POST /api/v1/user-books/
```

**Требуется:** Bearer токен  
**Статус ответа:** 201 (Created)  
**Тело запроса:**

```json
{
  "book_id": "uuid-book-1",
  "condition": "good",
  "status": "available"
}
```

#### Получить книгу из библиотеки

```
GET /api/v1/user-books/{userbook_id}
```

#### Обновить статус книги

```
PATCH /api/v1/user-books/{userbook_id}
```

**Требуется:** Bearer токен  
**Тело запроса:**

```json
{
  "condition": "acceptable",
  "status": "unavailable"
}
```

#### Удалить книгу из библиотеки

```
DELETE /api/v1/user-books/{userbook_id}
```

**Требуется:** Bearer токен

### Обмены (`/api/v1/exchanges/`)

#### Получить все обмены пользователя

```
GET /api/v1/exchanges/?skip=0&limit=50&status=pending
```

**Параметры:**

- `skip`: пропустить N записей
- `limit`: вернуть N записей
- `status`: фильтр по статусу (pending, accepted, rejected, completed, cancelled)

#### Создать запрос на обмен

```
POST /api/v1/exchanges/
```

**Требуется:** Bearer токен  
**Статус ответа:** 201 (Created)  
**Тело запроса:**

```json
{
  "requested_userbook_id": "uuid-userbook-1",
  "offered_userbook_id": "uuid-userbook-2",
  "message": "I would love to trade!"
}
```

#### Получить детали обмена

```
GET /api/v1/exchanges/{exchange_id}
```

#### Принять запрос на обмен

```
PATCH /api/v1/exchanges/{exchange_id}/accept
```

**Требуется:** Bearer токен  
**Статус ответа:** 200 (OK)

#### Отклонить запрос на обмен

```
PATCH /api/v1/exchanges/{exchange_id}/reject
```

**Требуется:** Bearer токен  
**Статус ответа:** 200 (OK)

#### Завершить обмен

```
PATCH /api/v1/exchanges/{exchange_id}/complete
```

**Требуется:** Bearer токен  
**Статус ответа:** 200 (OK)

### Сообщения (`/api/v1/messages/`)

#### Получить сообщения для обмена

```
GET /api/v1/messages/{exchange_id}?skip=0&limit=50
```

#### Отправить сообщение

```
POST /api/v1/messages/
```

**Требуется:** Bearer токен  
**Статус ответа:** 201 (Created)  
**Тело запроса:**

```json
{
  "exchange_id": "uuid-exchange-1",
  "message_text": "Let's meet tomorrow at 3 PM"
}
```

#### Отметить сообщение как прочитанное

```
PATCH /api/v1/messages/{message_id}/mark-read
```

**Требуется:** Bearer токен  
**Статус ответа:** 200 (OK)

---

## Логика предметной области

### Жизненный цикл обмена книгами

1. **Создание запроса** (статус: `pending`)
   - Пользователь A видит книгу пользователя B
   - Пользователь A создает запрос на обмен, предлагая свою книгу
   - Запрос отправляется пользователю B

2. **Рассмотрение запроса**
   - Пользователь B может принять (`accepted`) или отклонить (`rejected`) запрос
   - При отклонении — обмен заканчивается

3. **Завершение обмена** (статус: `completed`)
   - После принятия обе стороны обмениваются книгами
   - Обмен отмечается как завершенный
   - У обоих пользователей счетчик `total_swaps` увеличивается на 1
   - Обе книги переходят в статус `swapped`

4. **Отмена** (статус: `cancelled`)
   - Обмен может быть отменен на любом этапе

### Состояние книги в библиотеке

- **available** — книга доступна для обмена
- **swapped** — книга обменена
- **unavailable** — книга временно недоступна

### Условие книги

- **new** — новая, не читавшаяся
- **good** — в хорошем состоянии
- **acceptable** — приемлемое состояние (есть заломы, пометки)
- **poor** — плохое состояние (повреждена, но читаема)

---

## Pydantic схемы (примеры)

### UserCreate

```python
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str  # минимум 6 символов
    display_name: Optional[str] = None
    location: Optional[str] = None
    preferences: Optional[str] = None
    bio: Optional[str] = None
```

### UserOut

```python
class UserOut(BaseModel):
    id: int
    username: str
    display_name: Optional[str]
    email: str
    location: Optional[str]
    preferences: Optional[str]
    created_at: datetime
    bio: Optional[str]
    total_swaps: int
    is_active: bool

    class Config:
        from_attributes = True
```

### BookCreate

```python
class BookCreate(BaseModel):
    title: str
    authors: Optional[str] = None
    ISBN: Optional[str] = None
    description: Optional[str] = None
    published_year: Optional[int] = None
    page_count: Optional[int] = None
    genre_ids: List[str] = []  # UUID жанров
```

### UserBookCreate

```python
class UserBookCreate(BaseModel):
    book_id: str  # UUID
    condition: str  # "new", "good", "acceptable", "poor"
    status: str = "available"  # "available", "swapped", "unavailable"
```

### ExchangeCreate

```python
class ExchangeCreate(BaseModel):
    requested_userbook_id: str  # UUID книги, которую запрашиваю
    offered_userbook_id: str     # UUID книги, которую предлагаю
    message: Optional[str] = None
```

---

## Примеры использования API

### Регистрация и вход

```bash
# 1. Регистрация
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword",
    "display_name": "John Doe"
  }'

# 2. Вход в систему
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepassword"
  }'

# Ответ содержит access_token — используйте его в дальнейших запросах
```

### Работа с книгами

```bash
# 1. Получить все доступные книги
curl "http://localhost:8000/api/v1/books/?skip=0&limit=10"

# 2. Создать новую книгу (требуется авторизация)
curl -X POST "http://localhost:8000/api/v1/books/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Dune",
    "authors": "Frank Herbert",
    "ISBN": "0-441-13959-0",
    "description": "Epic science fiction novel",
    "published_year": 1965,
    "page_count": 680,
    "genre_ids": ["genre-id-1"]
  }'

# 3. Добавить книгу в свою библиотеку
curl -X POST "http://localhost:8000/api/v1/user-books/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": "book-id-from-step-2",
    "condition": "good",
    "status": "available"
  }'
```

### Обмен книгами

```bash
# 1. Просмотреть профиль пользователя и его книги
curl "http://localhost:8000/api/v1/users/1"

# 2. Создать запрос на обмен
curl -X POST "http://localhost:8000/api/v1/exchanges/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "requested_userbook_id": "userbook-id-from-other-user",
    "offered_userbook_id": "your-userbook-id",
    "message": "Would you like to trade?"
  }'

# 3. Получить входящие запросы на обмен
curl "http://localhost:8000/api/v1/exchanges/?status=pending" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Принять запрос на обмен
curl -X PATCH "http://localhost:8000/api/v1/exchanges/exchange-id/accept" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 5. Завершить обмен
curl -X PATCH "http://localhost:8000/api/v1/exchanges/exchange-id/complete" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Вывод

В результате лабораторной работы было реализовано полноценное серверное приложение по теме буккроссинга.

Проект включает:

- **Модель данных** с использованием SQLAlchemy и Pydantic;
- **CRUD-операции** для всех основных сущностей;
- **Связи** one-to-many и many-to-many с ассоциативными таблицами;
- **Систему миграций** базы данных через Alembic;
- **Аутентификацию и авторизацию** по JWT;
- **Пользовательский интерфейс** для основных сценариев работы.

Разработанное приложение соответствует тематике лабораторной работы и покрывает основной функционал сервиса для обмена книгами между пользователями.
