# загрузка списка URL и парсинг HTML.
from pathlib import Path

from bs4 import BeautifulSoup

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
    urls: list[str] = []
    for line in URLS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            urls.append(line)
    return urls[:limit]


def parse_title(html: str) -> tuple[str, str | None]:

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
