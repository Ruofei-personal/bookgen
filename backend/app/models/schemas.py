from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class BookMeta(BaseModel):
    id: str
    title: str
    author: str = ""
    description: str = ""
    status: Literal["ongoing", "completed"] = "ongoing"
    tags: list[str] = Field(default_factory=list)
    cover: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    latest_chapter_title: str | None = None
    latest_chapter_number: int | None = None


class BookListItem(BookMeta):
    pass


class ChapterMeta(BaseModel):
    id: str
    book_id: str
    number: int
    title: str
    slug: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    summary: str | None = None
    audio: str | None = None


class ChapterListItem(BaseModel):
    id: str
    number: int
    title: str
    slug: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    summary: str | None = None
    audio: str | None = None


class NavChapter(BaseModel):
    slug: str
    title: str
    number: int


class ChapterReadBody(BaseModel):
    meta: ChapterMeta
    content_html: str
    content_markdown: str | None = None


class ChapterReadResponse(BaseModel):
    chapter: ChapterReadBody
    prev: NavChapter | None = None
    next: NavChapter | None = None


class BookDetailResponse(BaseModel):
    book: BookMeta
    chapters: list[ChapterListItem]


class BooksListResponse(BaseModel):
    books: list[BookListItem]


class HealthResponse(BaseModel):
    status: str = "ok"
    content_root: str
