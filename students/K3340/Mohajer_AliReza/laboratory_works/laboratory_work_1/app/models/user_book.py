from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.exchange import Exchange
    from app.models.user import User
    from app.models.book import Book


class UserBook(Base):
    __tablename__ = "user_books"
    __table_args__ = (
        UniqueConstraint("user_id", "book_id", name="uq_user_book"),
        CheckConstraint(
            "status IN ('available', 'swapped', 'unavailable')",
            name="ck_userbook_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True
    )
    condition: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="available")
    added_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="userbooks")
    book: Mapped["Book"] = relationship(back_populates="userbooks")

    exchanges_as_requested: Mapped[list["Exchange"]] = relationship(
        back_populates="requested_userbook",
        foreign_keys="Exchange.requested_userbook_id",
    )
    exchanges_as_offered: Mapped[list["Exchange"]] = relationship(
        back_populates="offered_userbook",
        foreign_keys="Exchange.offered_userbook_id",
    )
