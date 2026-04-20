from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    # print(f"Hashing password: {password}")
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    # print(f"Verifying password: {password} with hash: {password_hash}")
    return pwd_context.verify(password, password_hash)


def create_access_token(*, user_id: int, username: str) -> str:
    # print(f"Creating access token for user: {user_id} with username: {username}")
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.jwt_expire_minutes)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "username": username,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "type": "access",
    }
    # print(f"Creating access token: {payload}")
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    # print(f"Decoding access token: {token}")
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
