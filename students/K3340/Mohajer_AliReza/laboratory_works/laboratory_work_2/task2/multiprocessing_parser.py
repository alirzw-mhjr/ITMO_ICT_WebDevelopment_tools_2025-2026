"""Задача 2. Параллельный парсинг веб-страниц с помощью multiprocessing.

Список URL делится на равные части, каждую часть обрабатывает отдельный процесс.
У каждого процесса свой интерпретатор Python и своё сетевое соединение, поэтому
запросы выполняются по-настоящему параллельно. Для I/O-bound задачи такой подход
тоже ускоряет работу, но по сравнению с threading он тяжелее: на запуск процессов
и передачу данных уходит больше ресурсов. Каждый процесс открывает собственную
сессию к SQLite, а timeout в db.py защищает от ошибки "database is locked" при
одновременной записи.
"""

from __future__ import annotations

import multiprocessing
import time

import requests

from db import init_db, save_book
from parser_utils import HEADERS, load_urls, parse_title

PROCESSES = 4


def parse_and_save(url: str) -> None:
    """Загружает страницу по URL, парсит заголовок и сохраняет его в БД."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        title, author = parse_title(response.text)
        added = save_book(title, author)
        status = "сохранено" if added else "уже есть"
        print(f"[multiprocessing] {status}: {title} ({url})")
    except Exception as exc:  # noqa: BLE001
        print(f"[multiprocessing] ОШИБКА {url}: {exc}")


def worker(urls: list[str]) -> None:
    """Обрабатывает свою часть списка URL последовательно (в отдельном процессе)."""
    for url in urls:
        parse_and_save(url)


def run(workers: int = PROCESSES) -> float:
    """Запускает парсинг в `workers` процессах. Возвращает время выполнения."""
    init_db()
    urls = load_urls()

    chunks = [urls[i::workers] for i in range(workers)]
    processes = [
        multiprocessing.Process(target=worker, args=(chunk,)) for chunk in chunks
    ]

    start_time = time.perf_counter()
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    return time.perf_counter() - start_time


if __name__ == "__main__":
    # Защита __main__ обязательна: на Windows процессы запускаются методом spawn,
    # и модуль повторно импортируется в каждом дочернем процессе.
    elapsed = run()
    print(f"[multiprocessing] процессов: {PROCESSES}")
    print(f"[multiprocessing] время выполнения: {elapsed:.4f} c")
