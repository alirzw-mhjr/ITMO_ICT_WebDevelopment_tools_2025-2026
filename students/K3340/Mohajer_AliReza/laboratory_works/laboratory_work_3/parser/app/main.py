# Сервис-парсер (Подзадача 1, п.4).
# Отдельное FastAPI-приложение, вызывается по HTTP: принимает URL, скачивает
# страницу, парсит заголовок и автора и сохраняет книгу в общую базу SQLite.

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from common.crud import save_book
from common.database import init_db
from common.parsing import extract_title, fetch_html

app = FastAPI(title="Parser Service", version="1.0.0")


class ParseRequest(BaseModel):
    url: str


@app.on_event("startup")
def on_startup() -> None:
    # Гарантируем, что таблица books существует.
    init_db()


@app.post("/parse")
def parse(body: ParseRequest) -> dict:
    """Загружает страницу по URL, парсит заголовок и сохраняет его в БД."""
    try:
        html = fetch_html(body.url)
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    title, authors = extract_title(html)
    result = save_book(title, authors)

    return {
        "message": "Parsing completed",
        "url": body.url,
        "title": result["title"],
        "authors": authors,
        "book_id": result["id"],
        "created": result["created"],
    }
