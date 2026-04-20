from __future__ import annotations

from pydantic import BaseModel, Field


class GenreCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class GenreUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)


class GenreOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
