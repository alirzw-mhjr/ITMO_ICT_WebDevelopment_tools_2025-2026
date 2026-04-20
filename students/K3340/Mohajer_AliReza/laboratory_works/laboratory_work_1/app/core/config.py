from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
import os


ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")


def _must_getenv(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


@dataclass(frozen=True)
class Settings:
    database_url: str = _must_getenv("DATABASE_URL")
    jwt_secret: str = _must_getenv("JWT_SECRET")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))


settings = Settings()
