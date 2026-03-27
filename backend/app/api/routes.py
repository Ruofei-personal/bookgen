import logging

from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import BookDetailResponse, BooksListResponse, ChapterReadResponse, HealthResponse
from app.services.content import ContentError, ContentService, get_content_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.get("/health", response_model=HealthResponse)
def health(service: ContentService = Depends(get_content_service)) -> HealthResponse:
    return HealthResponse(status="ok", content_root=str(service.root))


@router.get("/books", response_model=BooksListResponse)
def list_books(service: ContentService = Depends(get_content_service)) -> BooksListResponse:
    books = service.list_books()
    return BooksListResponse(books=books)


@router.get("/books/{book_id}", response_model=BookDetailResponse)
def get_book(book_id: str, service: ContentService = Depends(get_content_service)) -> BookDetailResponse:
    try:
        result = service.get_book(book_id)
    except ContentError as e:
        logger.warning("Book load error: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
    if result is None:
        raise HTTPException(status_code=404, detail="书籍不存在")
    book, chapters = result
    return BookDetailResponse(book=book, chapters=chapters)


@router.get("/books/{book_id}/chapters/{chapter_slug}", response_model=ChapterReadResponse)
def get_chapter(
    book_id: str,
    chapter_slug: str,
    service: ContentService = Depends(get_content_service),
) -> ChapterReadResponse:
    try:
        result = service.get_chapter(book_id, chapter_slug)
    except ContentError as e:
        logger.warning("Chapter content error: %s", e)
        raise HTTPException(status_code=503, detail=str(e)) from e
    if result is None:
        raise HTTPException(status_code=404, detail="章节不存在")
    return result
