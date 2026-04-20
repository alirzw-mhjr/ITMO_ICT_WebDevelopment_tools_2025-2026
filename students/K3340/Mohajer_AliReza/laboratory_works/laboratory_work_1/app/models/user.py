from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, Text, DateTime, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    preferences: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_swaps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    userbooks: Mapped[list["UserBook"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    requested_exchanges: Mapped[list["Exchange"]] = relationship(
        back_populates="requester",
        foreign_keys="Exchange.requester_id",
    )
    owned_exchanges: Mapped[list["Exchange"]] = relationship(
        back_populates="owner",
        foreign_keys="Exchange.owner_id",
    )
