export type BookStatus = "ongoing" | "completed";

export interface BookListItem {
  id: string;
  title: string;
  author: string;
  description: string;
  status: BookStatus;
  tags: string[];
  cover: string | null;
  created_at: string | null;
  updated_at: string | null;
  latest_chapter_title: string | null;
  latest_chapter_number: number | null;
}

export interface ChapterListItem {
  id: string;
  number: number;
  title: string;
  slug: string;
  created_at: string | null;
  updated_at: string | null;
  summary: string | null;
  audio: string | null;
}

export interface BooksListResponse {
  books: BookListItem[];
}

export interface BookDetailResponse {
  book: BookListItem;
  chapters: ChapterListItem[];
}

export interface ChapterMeta {
  id: string;
  book_id: string;
  number: number;
  title: string;
  slug: string;
  created_at: string | null;
  updated_at: string | null;
  summary: string | null;
  audio: string | null;
}

export interface ChapterReadBody {
  meta: ChapterMeta;
  content_html: string;
  content_markdown: string | null;
}

export interface NavChapter {
  slug: string;
  title: string;
  number: number;
}

export interface ChapterReadResponse {
  chapter: ChapterReadBody;
  prev: NavChapter | null;
  next: NavChapter | null;
}
