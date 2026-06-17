"""Главное FastAPI-приложение (Подзадачи 2 и 3).

Расширяет приложение из ЛР 1: помимо чтения книг из БД, добавлены эндпоинты для
вызова парсера:
- POST /api/parse        — синхронный вызов сервиса-парсера по HTTP (Подзадача 2);
- POST /api/parse/async  — постановка задачи в очередь Celery (Подзадача 3);
- GET  /api/parse/result/{task_id} — получение результата фоновой задачи.
"""

from __future__ import annotations

import os

import requests
from celery.result import AsyncResult
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from common.database import get_db, init_db
from common.models import Book
from web.app.celery_app import celery_app
from web.app.schemas import BookOut, ParseRequest, TaskAccepted, TaskResult
from web.app.tasks import parse_url_task

PARSER_URL = os.getenv("PARSER_URL", "http://parser:8001")

app = FastAPI(title="Bookcrossing API (lab 3)", version="1.0.0")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "web"}


@app.get("/api/books", response_model=list[BookOut])
def list_books(db: Session = Depends(get_db)) -> list[Book]:
    """Список книг из БД (в том числе добавленных парсером)."""
    return list(db.scalars(select(Book).order_by(Book.id.desc())).all())


@app.post("/api/parse")
def parse_sync(body: ParseRequest) -> dict:
    """Подзадача 2: синхронно вызвать сервис-парсер (в отдельном контейнере)."""
    try:
        response = requests.post(
            f"{PARSER_URL}/parse", json={"url": body.url}, timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/parse/async", response_model=TaskAccepted, status_code=202)
def parse_async(body: ParseRequest) -> TaskAccepted:
    """Подзадача 3: поставить парсинг в очередь Celery и сразу вернуть task_id."""
    task = parse_url_task.delay(body.url)
    return TaskAccepted(task_id=task.id, status="queued")


@app.get("/api/parse/result/{task_id}", response_model=TaskResult)
def parse_result(task_id: str) -> TaskResult:
    """Узнать статус и результат фоновой задачи по её task_id."""
    result = AsyncResult(task_id, app=celery_app)
    return TaskResult(
        task_id=task_id,
        status=result.status,  # PENDING / STARTED / SUCCESS / FAILURE / RETRY
        result=result.result if result.successful() else None,
    )
