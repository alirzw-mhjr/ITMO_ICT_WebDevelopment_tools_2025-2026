from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.schemas.book import UserBookOut


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    display_name: str | None = Field(default=None, max_length=100)
    email: EmailStr
    location: str | None = Field(default=None, max_length=100)
    preferences: str | None = None
    bio: str | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=100)
    preferences: str | None = None
    bio: str | None = None


class UserOut(BaseModel):
    id: int
    username: str
    display_name: str | None
    email: EmailStr
    location: str | None
    preferences: str | None
    created_at: datetime
    bio: str | None
    total_swaps: int
    is_active: bool

    model_config = {"from_attributes": True}


class UserDetailOut(UserOut):
    userbooks: list[UserBookOut] = Field(default_factory=list)


class ChangePasswordIn(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6, max_length=128)
