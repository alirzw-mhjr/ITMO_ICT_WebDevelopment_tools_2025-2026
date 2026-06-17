# Образ для web-сервиса, Celery worker и Celery beat (одна кодовая база).
FROM python:3.12-slim

# Не пишем .pyc и не буферизуем вывод (логи сразу видны в docker logs).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/code

WORKDIR /code

# Сначала зависимости — чтобы кэш слоёв переиспользовался при изменении кода.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем общий код и код web-сервиса.
COPY common ./common
COPY web ./web

EXPOSE 8000

# Команда по умолчанию — web-сервер. worker и beat переопределяют её в compose.
CMD ["uvicorn", "web.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
