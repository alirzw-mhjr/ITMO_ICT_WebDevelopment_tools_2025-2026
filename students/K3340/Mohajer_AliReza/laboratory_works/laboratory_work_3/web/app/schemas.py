# Pydantic-схемы web-приложения.

from pydantic import BaseModel


class ParseRequest(BaseModel):
    url: str


class BookOut(BaseModel):
    id: int
    title: str
    authors: str | None = None
    isbn: str | None = None
    description: str | None = None
    published_year: int | None = None
    page_count: int | None = None

    model_config = {"from_attributes": True}


class TaskAccepted(BaseModel):
    task_id: str
    status: str


class TaskResult(BaseModel):
    task_id: str
    status: str
    result: dict | None = None
