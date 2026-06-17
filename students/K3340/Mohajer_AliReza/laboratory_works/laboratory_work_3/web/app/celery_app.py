"""Конфигурация Celery (Подзадача 3, п.2 и п.5).

Celery — асинхронная очередь задач. Брокером и хранилищем результатов выступает
Redis. Здесь же настроено расписание периодических задач (celery beat).
"""

from __future__ import annotations

import os

from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "bookcrossing",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["web.app.tasks"],  # модуль с задачами
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,  # результаты задач хранятся в Redis 1 час
)

# Периодические задачи (celery beat): каждые 60 секунд считаем книги в БД.
celery_app.conf.beat_schedule = {
    "report-books-count-every-minute": {
        "task": "web.app.tasks.report_books_count",
        "schedule": 60.0,
    },
}
