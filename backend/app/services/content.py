import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import markdown
import nh3

from app.config import resolve_content_root
from app.models.schemas import (
    BookListItem,
    BookMeta,
    ChapterListItem,
    ChapterMeta,
    ChapterReadBody,
    ChapterReadResponse,
    NavChapter,
)

logger = logging.getLogger(__name__)

MD_EXTENSIONS = ["extra", "sane_lists", "nl2br", "fenced_code"]
NH3_TAGS = {
    "p", "br", "strong", "b", "em", "i", "h1", "h2", "h3", "h4", "h5", "h6",
    "blockquote", "ul", "ol", "li", "a", "code", "pre", "hr", "table", "thead",
    "tbody", "tr", "th", "td", "img",
}
NH3_ATTRIBUTES = {
    "a": {"href", "title"},
    "img": {"src", "alt", "title"},
    "code": {"class"},
    "pre": {"class"},
}


class ContentError(Exception):
    def __init__(self, message: str, *, cause: Exception | None = None):
        super().__init__(message)
        self.cause = cause


def _render_markdown_safe(text: str) -> str:
    raw = markdown.markdown(text, extensions=MD_EXTENSIONS)
    return nh3.clean(
        raw,
        tags=NH3_TAGS,
        attributes=NH3_ATTRIBUTES,
        url_schemes={"http", "https", "mailto"},
    )


class ContentService:
    def __init__(self, root: Path | None = None):
        self.root = root or resolve_content_root()

    def _book_dir(self, book_id: str) -> Path:
        return self.root / book_id

    def _load_book_json(self, book_dir: Path) -> BookMeta | None:
        path = book_dir / "book.json"
        if not path.is_file():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return BookMeta.model_validate(data)
        except (json.JSONDecodeError, OSError, ValueError) as e:
            logger.warning("Failed to read book.json at %s: %s", path, e)
            raise ContentError(f"书籍元数据损坏: {book_dir.name}", cause=e) from e

    def _meta_files(self, book_dir: Path) -> list[Path]:
        meta_dir = book_dir / "meta"
        if not meta_dir.is_dir():
            return []
        return sorted(meta_dir.glob("*.json"))

    def _load_chapter_meta(self, path: Path) -> ChapterMeta | None:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return ChapterMeta.model_validate(data)
        except (json.JSONDecodeError, OSError, ValueError) as e:
            logger.warning("Skip bad chapter meta %s: %s", path, e)
            return None

    def _chapter_md_path(self, book_dir: Path, number: int) -> Path:
        return book_dir / "chapters" / f"{number:03d}.md"

    def _load_chapter_markdown(self, book_dir: Path, number: int) -> str:
        path = self._chapter_md_path(book_dir, number)
        if not path.is_file():
            raise ContentError(f"章节正文缺失: {path.name}")
        try:
            return path.read_text(encoding="utf-8")
        except OSError as e:
            raise ContentError(f"无法读取章节文件: {path}", cause=e) from e

    def _ordered_chapters(self, book_dir: Path) -> list[ChapterMeta]:
        metas: list[ChapterMeta] = []
        for p in self._meta_files(book_dir):
            m = self._load_chapter_meta(p)
            if m:
                metas.append(m)
        metas.sort(key=lambda c: c.number)
        return metas

    def _fill_latest(self, book: BookMeta, chapters: list[ChapterMeta]) -> BookMeta:
        if not chapters:
            return book
        last = chapters[-1]
        data = book.model_dump()
        if data.get("latest_chapter_title") is None:
            data["latest_chapter_title"] = last.title
        if data.get("latest_chapter_number") is None:
            data["latest_chapter_number"] = last.number
        return BookMeta.model_validate(data)

    def list_books(self) -> list[BookListItem]:
        if not self.root.is_dir():
            logger.warning("Content root does not exist: %s", self.root)
            return []
        items: list[BookListItem] = []
        for child in sorted(self.root.iterdir()):
            if not child.is_dir():
                continue
            try:
                book = self._load_book_json(child)
                if not book:
                    continue
                chs = self._ordered_chapters(child)
                book = self._fill_latest(book, chs)
                items.append(BookListItem.model_validate(book.model_dump()))
            except ContentError as e:
                logger.warning("Skip book %s: %s", child.name, e)
                continue
        def _epoch(dt: datetime | None) -> float:
            if dt is None:
                return 0.0
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.timestamp()

        items.sort(key=lambda b: _epoch(b.updated_at), reverse=True)
        return items

    def get_book(self, book_id: str) -> tuple[BookMeta, list[ChapterListItem]] | None:
        book_dir = self._book_dir(book_id)
        if not book_dir.is_dir():
            return None
        try:
            book = self._load_book_json(book_dir)
        except ContentError:
            raise
        if not book:
            return None
        chs = self._ordered_chapters(book_dir)
        book = self._fill_latest(book, chs)
        listing = [
            ChapterListItem(
                id=c.id,
                number=c.number,
                title=c.title,
                slug=c.slug,
                created_at=c.created_at,
                updated_at=c.updated_at,
                summary=c.summary,
            )
            for c in chs
        ]
        return book, listing

    def get_chapter(self, book_id: str, chapter_slug: str) -> ChapterReadResponse | None:
        book_dir = self._book_dir(book_id)
        if not book_dir.is_dir():
            return None
        chs = self._ordered_chapters(book_dir)
        idx = next((i for i, c in enumerate(chs) if c.slug == chapter_slug), None)
        if idx is None:
            return None
        current = chs[idx]
        try:
            md = self._load_chapter_markdown(book_dir, current.number)
        except ContentError:
            raise
        html = _render_markdown_safe(md)
        body = ChapterReadBody(
            meta=current,
            content_html=html,
            content_markdown=None,
        )
        prev = (
            NavChapter(slug=chs[idx - 1].slug, title=chs[idx - 1].title, number=chs[idx - 1].number)
            if idx > 0
            else None
        )
        next_ = (
            NavChapter(slug=chs[idx + 1].slug, title=chs[idx + 1].title, number=chs[idx + 1].number)
            if idx + 1 < len(chs)
            else None
        )
        return ChapterReadResponse(chapter=body, prev=prev, next=next_)


def get_content_service() -> ContentService:
    return ContentService()
