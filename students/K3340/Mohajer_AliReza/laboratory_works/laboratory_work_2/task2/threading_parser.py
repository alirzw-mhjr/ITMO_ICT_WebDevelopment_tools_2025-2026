# Задача 2. Параллельный парсинг веб-страниц с помощью threading.
import threading
import time

import requests

from db import init_db, save_book
from parser_utils import HEADERS, load_urls, parse_title

THREADS = 4


def parse_and_save(url: str) -> None:
    # Загружает страницу по URL, парсит заголовок и сохраняет его в БД
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        # print(response.text)
        title, author = parse_title(response.text)
        added = save_book(title, author)
        status = "сохранено" if added else "уже есть"
        print(f"[threading] {status}: {title} ({url})")
    except Exception as exc:  # noqa: BLE001 — для наглядности логируем любую ошибку
        print(f"[threading] ОШИБКА {url}: {exc}")


def worker(urls: list[str]) -> None:
    # Обрабатывает свою часть списка URL последовательно
    for url in urls:
        parse_and_save(url)


def run(workers: int = THREADS) -> float:
    # Запускает парсинг в `workers` потоках. Возвращает время выполнения
    init_db()
    urls = load_urls()

    # Делим список URL на `workers` примерно равных частей (срезы с шагом).
    chunks = [urls[i::workers] for i in range(workers)]
    threads = [threading.Thread(target=worker, args=(chunk,)) for chunk in chunks]

    start_time = time.perf_counter()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return time.perf_counter() - start_time


if __name__ == "__main__":
    elapsed = run()
    print(f"[threading] потоков: {THREADS}")
    print(f"[threading] время выполнения: {elapsed:.4f} c")
