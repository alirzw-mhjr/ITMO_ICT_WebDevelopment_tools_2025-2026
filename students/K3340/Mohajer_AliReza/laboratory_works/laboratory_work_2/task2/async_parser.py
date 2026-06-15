"""Задача 2. Параллельный парсинг веб-страниц с помощью async/await (asyncio + aiohttp).

Все запросы создаются как корутины и запускаются через asyncio.gather в одном
потоке. Пока один запрос ждёт ответ сети, управление передаётся другим корутинам,
поэтому десятки страниц загружаются практически одновременно без накладных
расходов на потоки или процессы. Для I/O-bound задачи это самый лёгкий и обычно
самый быстрый подход. Сетевые запросы асинхронные (aiohttp), а парсинг (bs4) и
запись в SQLite — синхронные, поэтому их быстрые CPU-операции выполняются по ходу
корутины.
"""

from __future__ import annotations

import asyncio
import time

import aiohttp

from db import init_db, save_book
from parser_utils import HEADERS, load_urls, parse_title

# Ограничение числа одновременных запросов: если выпустить все корутины разом,
# сервер gutenberg.org начинает рвать часть соединений. Семафор держит не более
# CONCURRENCY запросов в полёте, что и быстро, и вежливо по отношению к серверу.
CONCURRENCY = 10


async def parse_and_save(
    session: aiohttp.ClientSession, semaphore: asyncio.Semaphore, url: str
) -> None:
    """Асинхронно загружает страницу, парсит заголовок и сохраняет его в БД."""
    try:
        async with semaphore:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                resp.raise_for_status()
                html = await resp.text()
        title, author = parse_title(html)
        added = save_book(title, author)
        status = "сохранено" if added else "уже есть"
        print(f"[async] {status}: {title} ({url})")
    except Exception as exc:  # noqa: BLE001
        print(f"[async] ОШИБКА {url}: {exc}")


async def run() -> float:
    """Запускает асинхронный парсинг всех URL. Возвращает время выполнения."""
    init_db()
    urls = load_urls()

    semaphore = asyncio.Semaphore(CONCURRENCY)
    start_time = time.perf_counter()
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        await asyncio.gather(
            *(parse_and_save(session, semaphore, url) for url in urls)
        )
    return time.perf_counter() - start_time


if __name__ == "__main__":
    elapsed = asyncio.run(run())
    print(f"[async] обработано URL: {len(load_urls())}")
    print(f"[async] время выполнения: {elapsed:.4f} c")
