from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Exchange(Base):
    __tablename__ = "exchanges"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'accepted', 'rejected', 'completed', 'cancelled')",
            name="ck_exchange_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    requester_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    requested_userbook_id: Mapped[int] = mapped_column(
        ForeignKey("user_books.id"), nullable=False
    )
    offered_userbook_id: Mapped[int] = mapped_column(
        ForeignKey("user_books.id"), nullable=False
    )

    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    requested_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    exchange_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    requester: Mapped["User"] = relationship(
        back_populates="requested_exchanges",
        foreign_keys=[requester_id],
    )
    owner: Mapped["User"] = relationship(
        back_populates="owned_exchanges",
        foreign_keys=[owner_id],
    )

    requested_userbook: Mapped["UserBook"] = relationship(
        foreign_keys=[requested_userbook_id],
        back_populates="exchanges_as_requested",
    )
    offered_userbook: Mapped["UserBook"] = relationship(
        foreign_keys=[offered_userbook_id],
        back_populates="exchanges_as_offered",
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="exchange", cascade="all, delete-orphan"
    )
