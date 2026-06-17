"""Логика парсинга веб-страницы (перенесена из лабораторной работы 2).

Здесь только «чистый» парсинг: скачать HTML и извлечь заголовок с автором.
Сохранение в БД вынесено отдельно (common/crud.py), а сетевой вызов —
синхронный (requests), как и в ЛР 2.
"""

from __future__ import annotations

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


def fetch_html(url: str, timeout: int = 30) -> str:
    """Загружает HTML-страницу по URL. Бросает исключение при ошибке HTTP."""
    response = requests.get(url, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.text


def extract_title(html: str) -> tuple[str, str | None]:
    """Извлекает (заголовок, автор) из HTML-страницы книги Gutenberg.

    Заголовок берётся из <h1> или <title>; формат "Название by Автор"
    разбивается на название и автора.
    """
    soup = BeautifulSoup(html, "html.parser")

    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        raw = h1.get_text(strip=True)
    elif soup.title and soup.title.string:
        raw = soup.title.string.strip().replace("| Project Gutenberg", "").strip()
    else:
        raw = "Unknown title"

    author: str | None = None
    if " by " in raw:
        title_part, author_part = raw.rsplit(" by ", 1)
        title = title_part.strip()
        author = author_part.strip() or None
    else:
        title = raw

    return title[:255], author
