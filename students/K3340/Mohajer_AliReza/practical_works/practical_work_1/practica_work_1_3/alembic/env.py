# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Загружаем .env файл
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

# Добавляем путь к приложению
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "app"))

# Импортируем модели
from app.models import SQLModel  # ← Теперь это должно работать
import app.models
import sqlmodel

# Конфигурация
config = context.config

# Берем URL из .env
database_url = os.getenv("DATABASE_URL", "sqlite:///./bookcrossing.db")
config.set_main_option("sqlalchemy.url", database_url)

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
