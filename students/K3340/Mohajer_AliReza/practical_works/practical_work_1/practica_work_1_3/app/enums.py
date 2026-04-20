# app/enums.py
from enum import Enum


class BookCondition(str, Enum):
    NEW = "new"
    GOOD = "good"
    USED = "used"
    DAMAGED = "damaged"


class ExchangeStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
