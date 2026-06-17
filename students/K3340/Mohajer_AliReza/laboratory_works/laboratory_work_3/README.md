# Лабораторная работа 3. Docker, источники данных и очереди

**Цель:** упаковать FastAPI-приложение в Docker, интегрировать парсер с базой
данных и научиться вызывать парсер через HTTP и через очередь (Celery + Redis).

## База данных

Используется **тот же SQLite, что и в лабораторной работе 1** — файл
`../laboratory_work_1/app.db`. Папка ЛР 1 монтируется в каждый контейнер как
`/lab1`, поэтому все сервисы работают с одной и той же базой и видят книги,
добавленные ещё в ЛР 2.

## Архитектура

Пять сервисов, поднимаются одной командой `docker compose up`:

| Сервис   | Образ / сборка      | Порт | Назначение                                              |
| -------- | ------------------- | ---- | ------------------------------------------------------- |
| `redis`  | redis:7-alpine      | 6379 | Брокер сообщений и хранилище результатов Celery         |
| `parser` | `parser/Dockerfile` | 8001 | Сервис-парсер, вызывается по HTTP (`POST /parse`)       |
| `web`    | `web/Dockerfile`    | 8005 | Основное API (вызов парсера синхронно и через очередь)  |
| `worker` | `web/Dockerfile`    | —    | Celery worker — выполняет фоновые задачи парсинга       |
| `beat`   | `web/Dockerfile`    | —    | Celery beat — запускает периодические задачи            |

> Отдельного контейнера для БД нет: база — это файл SQLite из ЛР 1,
> примонтированный во все сервисы как том (`/lab1`).

```
                    ┌─────────┐  HTTP POST /parse   ┌──────────┐
   client ──HTTP──► │  web    │ ──────────────────► │  parser  │ ──► /lab1/app.db
                    │ (8005)  │                     │  (8001)  │      (SQLite, ЛР1)
                    └────┬────┘                     └──────────┘
                         │ .delay(url)                   ▲
                         ▼                               │ HTTP POST /parse
                    ┌─────────┐   берёт задачу     ┌──────────┐
                    │  redis  │ ◄───────────────── │  worker  │
                    └─────────┘                    └──────────┘
                         ▲ расписание (60с)
                         │
                    ┌─────────┐
                    │  beat   │  → periodic task report_books_count
                    └─────────┘
```

Запись в БД делает только сервис `parser`. И синхронный эндпоинт `web`, и
фоновая задача Celery обращаются к нему по HTTP — поэтому парсер единственный
источник истины, а запись в SQLite идёт через один процесс (без конфликтов
блокировок).

## Структура проекта

```
laboratory_work_3/
├── docker-compose.yml          # оркестрация всех сервисов
├── requirements.txt            # общие зависимости (для обоих образов)
├── .env.example
├── .dockerignore
├── common/                     # общий код (БД, модели, парсинг)
│   ├── database.py             # engine SQLite, сессии, init_db
│   ├── models.py               # модель Book (как в ЛР 1)
│   ├── crud.py                 # save_book, count_books
│   └── parsing.py              # fetch_html + extract_title (из ЛР 2)
├── parser/
│   ├── Dockerfile
│   └── app/main.py             # FastAPI парсер: POST /parse
└── web/
    ├── Dockerfile
    └── app/
        ├── main.py             # FastAPI API: /api/parse, /api/parse/async ...
        ├── schemas.py
        ├── celery_app.py       # конфигурация Celery + расписание beat
        └── tasks.py            # задачи parse_url_task, report_books_count
```

## Запуск

> Требуется установленный и **запущенный Docker Desktop**.

```bash
cd laboratory_work_3
docker compose up --build
```

После старта:

- API (Swagger): <http://localhost:8005/docs>
- Парсер (Swagger): <http://localhost:8001/docs>

Остановить: `Ctrl+C`, затем `docker compose down`.

## Проверка работы

### Подзадача 1 — парсер по HTTP (напрямую)

```bash
curl -X POST http://localhost:8001/parse \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://www.gutenberg.org/ebooks/345\"}"
```

### Подзадача 2 — синхронный вызов парсера из web

```bash
curl -X POST http://localhost:8005/api/parse \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://www.gutenberg.org/ebooks/1342\"}"
```

`web` обращается к контейнеру `parser` по адресу `http://parser:8001/parse` и
возвращает результат клиенту.

### Подзадача 3 — асинхронный вызов через очередь Celery

```bash
# 1. поставить задачу в очередь — сразу вернётся task_id
curl -X POST http://localhost:8005/api/parse/async \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://www.gutenberg.org/ebooks/84\"}"

# 2. узнать статус/результат задачи
curl http://localhost:8005/api/parse/result/<task_id>
```

### Проверить сохранённые книги

```bash
curl http://localhost:8005/api/books
```

Здесь же видны книги, добавленные ещё в ЛР 2, — это та же база SQLite.

### Периодическая задача

`beat` каждые 60 секунд ставит задачу `report_books_count`, а `worker`
её выполняет и пишет в лог число книг:

```bash
docker compose logs -f worker
```

## Переменные окружения

Заданы прямо в `docker-compose.yml` (см. `.env.example`):

- `DATABASE_URL` — путь к SQLite (`sqlite:////lab1/app.db`);
- `REDIS_URL` — адрес Redis (брокер + backend Celery);
- `PARSER_URL` — адрес сервиса-парсера для `web` и `worker`.

## Соответствие заданию

- **Подзадача 1** — Dockerfile для web и parser, `docker-compose.yml`; база
  данных — SQLite из ЛР 1 (том `/lab1`); парсер вызывается по HTTP
  (`POST /parse`).
- **Подзадача 2** — эндпоинт `POST /api/parse` вызывает парсер в отдельном
  контейнере и возвращает результат.
- **Подзадача 3** — Celery + Redis, задача `parse_url_task`, сервисы `worker` и
  `beat` в compose, эндпоинт `POST /api/parse/async`, периодическая задача
  `report_books_count` по расписанию.
