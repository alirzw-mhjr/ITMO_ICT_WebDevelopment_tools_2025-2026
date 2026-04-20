from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import auth, books, exchanges, genres, user_books, users


api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(genres.router, prefix="/genres", tags=["genres"])
api_router.include_router(books.router, prefix="/books", tags=["books"])
api_router.include_router(user_books.router, prefix="/user-books", tags=["user-books"])
api_router.include_router(exchanges.router, prefix="/exchanges", tags=["exchanges"])
