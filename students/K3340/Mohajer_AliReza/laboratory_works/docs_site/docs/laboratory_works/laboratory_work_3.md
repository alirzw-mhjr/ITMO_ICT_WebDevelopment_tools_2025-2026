# Лабораторная работа 3. Docker, источники данных и очереди

## Цель работы

Научиться упаковывать FastAPI-приложение в Docker, интегрировать парсер данных с
базой данных и вызывать парсер двумя способами: напрямую по HTTP и асинхронно
через очередь задач (Celery + Redis).

## Что переиспользовано из прошлых работ

- **FastAPI-приложение и база данных** — из лабораторной работы 1 (модель `Book`,
  работа через SQLAlchemy).
- **Парсер** — из лабораторной работы 2 (загрузка страницы Project Gutenberg и
  извлечение заголовка с автором через BeautifulSoup).

В ЛР 3 всё это упаковано в контейнеры и дополнено вызовом парсера по HTTP и через
очередь.

## Архитектура

Система состоит из пяти сервисов, описанных в `docker-compose.yml`:

| Сервис   | Образ / сборка     | Порт | Назначение                                        |
| -------- | ------------------ | ---- | ------------------------------------------------- |
| `redis`  | redis:7-alpine     | 6379 | Брокер сообщений и backend результатов Celery     |
| `parser` | parser/Dockerfile  | 8001 | Сервис-парсер, вызывается по HTTP                  |
| `web`    | web/Dockerfile     | 8005 | Основное API                                      |
| `worker` | web/Dockerfile     | —    | Celery worker — фоновое выполнение задач          |
| `beat`   | web/Dockerfile     | —    | Celery beat — периодические задачи по расписанию  |

Отдельного контейнера для БД нет: используется **тот же SQLite, что и в ЛР 1** —
файл `../laboratory_work_1/app.db`, примонтированный во все сервисы как `/lab1`.
Благодаря этому в ЛР 3 видны и книги, добавленные ещё в ЛР 2.

```
client ──► web (8005) ──HTTP──► parser (8001) ──► /lab1/app.db (SQLite, ЛР1)
              │
              │ .delay(url)
              ▼
            redis ◄── worker ──HTTP──► parser (8001) ──► /lab1/app.db
              ▲
              │ расписание 60с
            beat
```

Вся логика парсинга находится в сервисе `parser`. И синхронный эндпоинт, и
фоновая задача Celery обращаются к нему по HTTP — парсер остаётся единственным
местом, где скачивается и разбирается страница.

---

## Подзадача 1. Упаковка в Docker

### Парсер, вызываемый по HTTP

Отдельное FastAPI-приложение (`parser/app/main.py`) с эндпоинтом `POST /parse`:
принимает URL, скачивает страницу, парсит заголовок и автора и сохраняет книгу
в БД.

```python
@app.post("/parse")
def parse(body: ParseRequest) -> dict:
    try:
        html = fetch_html(body.url)
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    title, authors = extract_title(html)
    result = save_book(title, authors)
    return {"message": "Parsing completed", "title": result["title"], ...}
```

### Dockerfile

Для `web` и `parser` написаны отдельные Dockerfile. Базовый образ —
`python:3.12-slim`; сначала ставятся зависимости (кэшируемый слой), затем
копируется код, в конце задаётся команда запуска через `uvicorn`.

```dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/code
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY common ./common
COPY web ./web
CMD ["uvicorn", "web.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Зачем Docker:** упаковка приложения вместе со всеми зависимостями в единый
образ обеспечивает одинаковую среду выполнения на любой машине и упрощает
развёртывание.

### Docker Compose

`docker-compose.yml` поднимает все сервисы одной командой, задаёт порты,
переменные окружения и зависимости между сервисами (`depends_on` с проверкой
`service_healthy` для Redis). База данных — файл SQLite из ЛР 1, примонтированный
во все сервисы как том `/lab1`.

**Зачем Compose:** управление несколькими контейнерами через один файл
конфигурации — запуск, сеть, порядок старта.

---

## Подзадача 2. Вызов парсера из FastAPI

В основное приложение добавлен эндпоинт `POST /api/parse`, который принимает URL
от клиента, обращается к сервису-парсеру в отдельном контейнере по адресу
`http://parser:8001/parse` и возвращает результат клиенту.

```python
@app.post("/api/parse")
def parse_sync(body: ParseRequest) -> dict:
    response = requests.post(f"{PARSER_URL}/parse", json={"url": body.url}, timeout=60)
    response.raise_for_status()
    return response.json()
```

**Зачем:** функциональность парсера интегрируется в веб-приложение — пользователь
запускает парсинг через общий API.

---

## Подзадача 3. Вызов парсера через очередь (Celery + Redis)

### Как это работает

Celery — асинхронная очередь задач. При получении запроса задача кладётся в
очередь Redis, а Celery-worker берёт её и выполняет в фоне. Клиент не ждёт
завершения долгой операции.

### Конфигурация Celery

```python
celery_app = Celery("bookcrossing", broker=REDIS_URL, backend=REDIS_URL,
                    include=["web.app.tasks"])
```

### Фоновая задача парсинга

```python
@celery_app.task(name="web.app.tasks.parse_url_task", bind=True, max_retries=2)
def parse_url_task(self, url: str) -> dict:
    try:
        response = requests.post(f"{PARSER_URL}/parse", json={"url": url}, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise self.retry(exc=exc, countdown=5)
```

### Эндпоинт асинхронного вызова

```python
@app.post("/api/parse/async", status_code=202)
def parse_async(body: ParseRequest):
    task = parse_url_task.delay(body.url)
    return {"task_id": task.id, "status": "queued"}
```

Результат задачи запрашивается отдельно: `GET /api/parse/result/{task_id}`.

**Зачем:** парсинг выполняется в фоне, API сразу отвечает клиенту — это улучшает
отзывчивость приложения.

### Периодические задачи (celery beat)

Настроено расписание: каждые 60 секунд выполняется задача `report_books_count`,
которая считает книги в БД и пишет результат в лог.

```python
celery_app.conf.beat_schedule = {
    "report-books-count-every-minute": {
        "task": "web.app.tasks.report_books_count",
        "schedule": 60.0,
    },
}
```

**Зачем:** периодические задачи нужны для регулярных операций — обновления
данных, очистки БД, отправки уведомлений.

### Обновление Docker Compose

В `docker-compose.yml` добавлены сервисы `redis`, `worker` (Celery worker) и
`beat` (Celery beat). `worker` и `beat` используют тот же образ, что и `web`, но
с разными командами запуска, и зависят от `redis`.

---

## Запуск и проверка

```bash
cd laboratory_work_3
docker compose up --build
```

| Действие                      | Запрос                                              |
| ----------------------------- | --------------------------------------------------- |
| Парсер напрямую               | `POST http://localhost:8001/parse`                  |
| Синхронный вызов из web       | `POST http://localhost:8005/api/parse`              |
| Асинхронный вызов (очередь)   | `POST http://localhost:8005/api/parse/async`        |
| Результат фоновой задачи      | `GET http://localhost:8005/api/parse/result/{id}`   |
| Список книг                   | `GET http://localhost:8005/api/books`               |
| Логи периодической задачи     | `docker compose logs -f worker`                     |

Swagger доступен на <http://localhost:8005/docs> (API) и
<http://localhost:8001/docs> (парсер).

---

## Вывод

В работе FastAPI-приложение из ЛР 1 и парсер из ЛР 2 упакованы в
Docker-контейнеры и объединены через Docker Compose, а данные сохраняются в ту же
базу SQLite, что была создана в ЛР 1. Парсер вынесен в отдельный
сервис и вызывается тремя способами: напрямую по HTTP, синхронно из основного
API и асинхронно через очередь Celery с брокером Redis. Дополнительно настроены
периодические задачи по расписанию. Такая архитектура показывает разницу между
синхронной интеграцией сервисов и фоновой обработкой задач в очереди.
