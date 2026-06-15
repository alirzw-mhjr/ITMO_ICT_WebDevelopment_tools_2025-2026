# Лабораторная работа 2. Потоки. Процессы. Асинхронность

**Цель работы:** понять отличия между потоками и процессами и разобраться,
что такое асинхронность в Python.

## Структура

```
laboratory_work_2/
├── task1/                      # Задача 1. Подсчёт суммы чисел
│   ├── threading_sum.py
│   ├── multiprocessing_sum.py
│   └── async_sum.py
└── task2/                      # Задача 2. Параллельный парсинг веб-страниц
    ├── db.py                   # Подключение к БД из ЛР 1 + сохранение книг
    ├── parser_utils.py         # Загрузка списка URL и парсинг заголовка
    ├── threading_parser.py
    ├── multiprocessing_parser.py
    ├── async_parser.py
    ├── book_urls.txt           # Список URL для парсинга
    └── requirements.txt
```

## Задача 1. Различия между threading, multiprocessing и async

Три программы считают сумму чисел от 1 до N, разбивая диапазон на несколько
параллельных подзадач. Это **CPU-bound** задача.

```bash
cd task1
python threading_sum.py
python multiprocessing_sum.py
python async_sum.py
```

> Полное N = 10^13 в чистом Python считается очень долго. Для замеров значение
> `TARGET` в начале файлов удобно уменьшить (например, до `10**8`), сохранив
> структуру программ.

Вывод: на CPU-bound задаче выигрывает **multiprocessing** (реальный параллелизм
на ядрах), а threading и async из-за GIL не дают ускорения.

## Задача 2. Параллельный парсинг веб-страниц

Три программы параллельно загружают страницы книг с
[Project Gutenberg](https://www.gutenberg.org/), парсят заголовок и автора и
сохраняют их в таблицу `books` базы данных из **лабораторной работы 1**
(`laboratory_work_1/app.db`). Это **I/O-bound** задача.

### Запуск

```bash
cd task2
pip install -r requirements.txt
python threading_parser.py
python multiprocessing_parser.py
python async_parser.py
```

> **Windows:** если в консоли возникает `UnicodeEncodeError` при выводе
> кириллицы, установите переменную окружения `PYTHONIOENCODING=utf-8`
> (в PowerShell: `$env:PYTHONIOENCODING="utf-8"`).

Число обрабатываемых URL задаётся константой `URL_LIMIT` в `parser_utils.py`
(по умолчанию 30 из ~950, чтобы прогон занимал разумное время).

Вывод: на I/O-bound задаче выигрывает **async**, threading тоже даёт ускорение,
а multiprocessing работает, но тяжелее остальных.

Подробное сравнение и таблицы времени — в документации mkdocs
(`docs_site/docs/laboratory_works/laboratory_work_2.md`).
