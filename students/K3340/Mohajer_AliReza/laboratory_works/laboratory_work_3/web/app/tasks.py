"""Задачи Celery (Подзадача 3).

- parse_url_task — фоновая задача парсинга: обращается к сервису-парсеру по HTTP
  (тому же, что вызывается синхронно), поэтому вся логика парсинга остаётся в
  одном месте.
- report_books_count — периодическая задача: раз в минуту считает книги в БД
  (пример регулярной операции по расписанию).
"""

import logging
import os

import requests

from common.crud import count_books
from web.app.celery_app import celery_app

logger = logging.getLogger(__name__)

PARSER_URL = os.getenv("PARSER_URL", "http://parser:8001")


@celery_app.task(name="web.app.tasks.parse_url_task", bind=True, max_retries=2)
def parse_url_task(self, url: str) -> dict:
    """Фоновая задача: просит сервис-парсер обработать URL и сохранить книгу."""
    try:
        response = requests.post(f"{PARSER_URL}/parse", json={"url": url}, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        # При сетевой ошибке пробуем ещё раз с задержкой.
        logger.warning("parse_url_task failed for %s: %s", url, exc)
        raise self.retry(exc=exc, countdown=5)


@celery_app.task(name="web.app.tasks.report_books_count")
def report_books_count() -> dict:
    """Периодическая задача: логирует текущее количество книг в БД."""
    total = count_books()
    logger.info("Periodic task: в базе сейчас %s книг", total)
    return {"books": total}
