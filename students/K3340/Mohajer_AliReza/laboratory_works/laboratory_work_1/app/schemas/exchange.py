from __future__ import annotations

from datetime import datetime

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.book import UserBookOut
from app.schemas.user import UserOut


class ExchangeCreate(BaseModel):
    requested_userbook_id: int
    offered_userbook_id: int
    message: str | None = None


class ExchangeUpdateStatus(BaseModel):
    status: Literal["pending", "accepted", "rejected", "completed", "cancelled"]


class ExchangeOut(BaseModel):
    id: int
    requester: UserOut
    owner: UserOut
    requested_userbook: UserBookOut
    offered_userbook: UserBookOut
    message: str | None
    status: str
    requested_at: datetime
    exchange_at: datetime | None

    model_config = {"from_attributes": True}


class MessageCreateBody(BaseModel):
    message_text: str = Field(min_length=1)


class MessageOut(BaseModel):
    id: int
    exchange_id: int
    sender_id: int
    receiver_id: int
    message_text: str
    is_read: bool
    sent_at: datetime

    model_config = {"from_attributes": True}


class ExchangeDetailOut(ExchangeOut):
    messages: list[MessageOut] = Field(default_factory=list)
