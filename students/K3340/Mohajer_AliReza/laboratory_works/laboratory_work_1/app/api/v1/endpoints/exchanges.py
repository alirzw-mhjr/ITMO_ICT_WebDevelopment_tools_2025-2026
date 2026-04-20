from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.models.book import Book
from app.models.user_book import UserBook
from app.models.exchange import Exchange
from app.models.message import Message
from app.schemas.exchange import (
    ExchangeCreate,
    ExchangeDetailOut,
    ExchangeOut,
    ExchangeUpdateStatus,
    MessageCreateBody,
    MessageOut,
)

router = APIRouter()


def _exchange_base_options():
    return (
        selectinload(Exchange.requester),
        selectinload(Exchange.owner),
        selectinload(Exchange.requested_userbook)
        .selectinload(UserBook.book)
        .selectinload(Book.genres),
        selectinload(Exchange.offered_userbook)
        .selectinload(UserBook.book)
        .selectinload(Book.genres),
    )


def _exchange_detail_options():
    return _exchange_base_options() + (selectinload(Exchange.messages),)


@router.get("/mine", response_model=list[ExchangeOut])
def my_exchanges(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[Exchange]:
    q = (
        select(Exchange)
        .where(
            or_(Exchange.requester_id == current.id, Exchange.owner_id == current.id)
        )
        .options(*_exchange_base_options())
        .order_by(Exchange.requested_at.desc())
    )
    return list(db.scalars(q).all())


@router.post("", response_model=ExchangeOut, status_code=201)
def create_exchange(
    body: ExchangeCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> Exchange:
    requested = db.scalar(
        select(UserBook)
        .where(UserBook.id == body.requested_userbook_id)
        .options(selectinload(UserBook.book)),
    )
    offered = db.scalar(
        select(UserBook)
        .where(UserBook.id == body.offered_userbook_id)
        .options(selectinload(UserBook.book)),
    )
    if requested is None or offered is None:
        raise HTTPException(status_code=404, detail="User book not found")
    if offered.user_id != current.id:
        raise HTTPException(
            status_code=403, detail="Offered book must be from your library"
        )
    if requested.user_id == current.id:
        raise HTTPException(status_code=400, detail="Cannot request your own book")
    if requested.status != "available" or offered.status != "available":
        raise HTTPException(status_code=400, detail="Both books must be available")

    ex = Exchange(
        requester_id=current.id,
        owner_id=requested.user_id,
        requested_userbook_id=requested.id,
        offered_userbook_id=offered.id,
        message=body.message,
    )
    db.add(ex)
    db.commit()
    out = db.scalar(
        select(Exchange).where(Exchange.id == ex.id).options(*_exchange_base_options())
    )
    assert out is not None
    return out


@router.get("/{exchange_id}", response_model=ExchangeDetailOut)
def get_exchange(
    exchange_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> Exchange:
    ex = db.scalar(
        select(Exchange)
        .where(Exchange.id == exchange_id)
        .options(*_exchange_detail_options()),
    )
    if ex is None:
        raise HTTPException(status_code=404, detail="Exchange not found")
    if current.id not in (ex.requester_id, ex.owner_id):
        raise HTTPException(
            status_code=403, detail="Not a participant of this exchange"
        )
    return ex


@router.patch("/{exchange_id}/status", response_model=ExchangeOut)
def update_exchange_status(
    exchange_id: int,
    body: ExchangeUpdateStatus,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> Exchange:
    ex = db.scalar(
        select(Exchange)
        .where(Exchange.id == exchange_id)
        .options(*_exchange_base_options()),
    )
    if ex is None:
        raise HTTPException(status_code=404, detail="Exchange not found")
    if current.id not in (ex.requester_id, ex.owner_id):
        raise HTTPException(
            status_code=403, detail="Not a participant of this exchange"
        )

    new_status = body.status
    if new_status == ex.status:
        return ex

    if new_status == "accepted":
        if current.id != ex.owner_id:
            raise HTTPException(status_code=403, detail="Only the owner can accept")
        if ex.status != "pending":
            raise HTTPException(
                status_code=400, detail="Only pending exchanges can be accepted"
            )
        ex.status = "accepted"
        ex.exchange_at = datetime.utcnow()
        ex.requested_userbook.status = "swapped"
        ex.offered_userbook.status = "swapped"
    elif new_status == "rejected":
        if current.id != ex.owner_id:
            raise HTTPException(status_code=403, detail="Only the owner can reject")
        if ex.status != "pending":
            raise HTTPException(
                status_code=400, detail="Only pending exchanges can be rejected"
            )
        ex.status = "rejected"
    elif new_status == "cancelled":
        if current.id != ex.requester_id:
            raise HTTPException(status_code=403, detail="Only the requester can cancel")
        if ex.status != "pending":
            raise HTTPException(
                status_code=400, detail="Only pending exchanges can be cancelled"
            )
        ex.status = "cancelled"
    elif new_status == "completed":
        if ex.status != "accepted":
            raise HTTPException(
                status_code=400, detail="Only accepted exchanges can be completed"
            )
        ex.status = "completed"
        ex.requester.total_swaps += 1
        ex.owner.total_swaps += 1
    elif new_status == "pending":
        raise HTTPException(status_code=400, detail="Cannot set status back to pending")
    else:
        raise HTTPException(status_code=400, detail="Unsupported status transition")

    db.add(ex)
    db.commit()
    out = db.scalar(
        select(Exchange).where(Exchange.id == ex.id).options(*_exchange_base_options())
    )
    assert out is not None
    return out


@router.get("/{exchange_id}/messages", response_model=list[MessageOut])
def list_messages(
    exchange_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[Message]:
    ex = db.get(Exchange, exchange_id)
    if ex is None:
        raise HTTPException(status_code=404, detail="Exchange not found")
    if current.id not in (ex.requester_id, ex.owner_id):
        raise HTTPException(
            status_code=403, detail="Not a participant of this exchange"
        )
    return list(
        db.scalars(
            select(Message)
            .where(Message.exchange_id == exchange_id)
            .order_by(Message.sent_at.asc()),
        ).all(),
    )


@router.post("/{exchange_id}/messages", response_model=MessageOut, status_code=201)
def send_message(
    exchange_id: int,
    body: MessageCreateBody,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> Message:
    ex = db.get(Exchange, exchange_id)
    if ex is None:
        raise HTTPException(status_code=404, detail="Exchange not found")
    if current.id not in (ex.requester_id, ex.owner_id):
        raise HTTPException(
            status_code=403, detail="Not a participant of this exchange"
        )
    receiver_id = ex.owner_id if current.id == ex.requester_id else ex.requester_id
    msg = Message(
        exchange_id=exchange_id,
        sender_id=current.id,
        receiver_id=receiver_id,
        message_text=body.message_text,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
