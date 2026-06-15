"""Вспомогательные функции для задачи 2: загрузка списка URL и парсинг HTML.

Логика разбора страницы вынесена сюда, чтобы все три варианта парсера
(threading, multiprocessing, async) извлекали заголовок книги одинаково.
"""

from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup

# Сколько URL из book_urls.txt реально обрабатывать. В файле ~950 ссылок;
# для замеров и сравнения подходов берём первые URL_LIMIT штук, чтобы прогон
# занимал разумное время и не создавал лишнюю нагрузку на gutenberg.org.
URL_LIMIT = 30

URLS_FILE = Path(__file__).resolve().parent / "book_urls.txt"

# User-Agent, чтобы запросы не отклонялись как «не-браузерные».
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


def load_urls(limit: int = URL_LIMIT) -> list[str]:
    """Читает book_urls.txt и возвращает первые `limit` непустых ссылок."""
    urls: list[str] = []
    for line in URLS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            urls.append(line)
    return urls[:limit]


def parse_title(html: str) -> tuple[str, str | None]:
    """Извлекает (заголовок, автор) из HTML-страницы книги Gutenberg.

    У страниц вида https://www.gutenberg.org/ebooks/<id> заголовок лежит в
    <h1>, а тег <title> имеет формат "Название | Project Gutenberg".
    Автора берём из строки вида "Название by Автор", если она есть.
    """
    soup = BeautifulSoup(html, "html.parser")

    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        raw = h1.get_text(strip=True)
    elif soup.title and soup.title.string:
        raw = soup.title.string.strip()
        raw = raw.replace("| Project Gutenberg", "").strip()
    else:
        raw = "Unknown title"

    # Формат Gutenberg: "Название by Автор" — разделяем по " by ".
    author: str | None = None
    if " by " in raw:
        title_part, author_part = raw.rsplit(" by ", 1)
        title = title_part.strip()
        author = author_part.strip() or None
    else:
        title = raw

    return title[:255], author
