import { getApiBase } from "./env";
import type {
  BookDetailResponse,
  BooksListResponse,
  ChapterReadResponse,
} from "./types";

const REVALIDATE = 30;

async function apiGet<T>(path: string): Promise<{ data: T | null; notFound: boolean }> {
  const url = `${getApiBase()}${path}`;
  const res = await fetch(url, {
    next: { revalidate: REVALIDATE },
  });
  if (res.status === 404) {
    return { data: null, notFound: true };
  }
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text.slice(0, 200)}`);
  }
  const data = (await res.json()) as T;
  return { data, notFound: false };
}

export async function fetchBooks(): Promise<BooksListResponse> {
  const { data, notFound } = await apiGet<BooksListResponse>("/api/books");
  if (notFound || !data) {
    return { books: [] };
  }
  return data;
}

export async function fetchBook(
  bookId: string,
): Promise<BookDetailResponse | null> {
  const { data, notFound } = await apiGet<BookDetailResponse>(
    `/api/books/${encodeURIComponent(bookId)}`,
  );
  if (notFound || !data) return null;
  return data;
}

export async function fetchChapter(
  bookId: string,
  chapterSlug: string,
): Promise<ChapterReadResponse | null> {
  const { data, notFound } = await apiGet<ChapterReadResponse>(
    `/api/books/${encodeURIComponent(bookId)}/chapters/${encodeURIComponent(chapterSlug)}`,
  );
  if (notFound || !data) return null;
  return data;
}
