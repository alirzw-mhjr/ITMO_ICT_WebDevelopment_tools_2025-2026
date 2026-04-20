# Bookcrossing FastAPI (Lab 1)

## Setup

Python 3.10+

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## Migrations (Alembic)

Initialize DB schema:

```bash
alembic upgrade head
```

Generate a new migration after model changes:

```bash
alembic revision --autogenerate -m "your message"
alembic upgrade head
```

## Run

```bash
uvicorn app.main:app --reload
```

Open docs: `/docs`

## API overview

- **Auth** (`/auth`): `POST /register`, `POST /login` (JWT), `GET /me`, `POST /change-password`
- **Users** (`/users`): `GET /` (list), `GET /{user_id}` (profile + nested `userbooks` → `book` → `genres`), `PATCH /me` (profile)
- **Genres** (`/genres`): full CRUD
- **Books** (`/books`): full CRUD; responses include nested `genres` (many-to-many)
- **Library** (`/user-books`): `GET /mine`, `GET /catalog` (search available copies), CRUD on your items
- **Exchanges** (`/exchanges`): `GET /mine`, `POST /`, `GET /{id}` (with nested `messages`), `PATCH /{id}/status`, `GET|POST /{id}/messages`

Authenticated requests: header `Authorization: Bearer <access_token>`.

