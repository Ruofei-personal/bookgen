import Link from "next/link";
import { assetUrl } from "@/lib/env";
import type { BookListItem } from "@/lib/types";

function formatTime(iso: string | null) {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    return d.toLocaleDateString("zh-CN", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return iso;
  }
}

export function BookCard({ book }: { book: BookListItem }) {
  const coverSrc = book.cover?.startsWith("/content/") ? book.cover : assetUrl(book.cover);
  const statusLabel = book.status === "completed" ? "完结" : "连载";

  return (
    <article className="group rounded-xl border border-zinc-200/90 bg-white p-4 shadow-sm transition hover:border-zinc-300 dark:border-zinc-800 dark:bg-zinc-900/40 dark:hover:border-zinc-700 sm:p-5">
      <div className="flex flex-col gap-4 sm:flex-row">
        <div className="relative mx-auto h-40 w-28 shrink-0 overflow-hidden rounded-lg bg-zinc-100 dark:bg-zinc-800 sm:mx-0">
          {coverSrc ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={coverSrc} alt="" className="h-full w-full object-cover" />
          ) : (
            <div className="flex h-full items-center justify-center text-xs text-zinc-400">
              无封面
            </div>
          )}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <Link
              href={`/books/${book.id}`}
              className="text-lg font-semibold text-zinc-900 hover:underline dark:text-zinc-50"
            >
              {book.title}
            </Link>
            <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">
              {statusLabel}
            </span>
          </div>
          {book.author ? (
            <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">{book.author}</p>
          ) : null}
          <p className="mt-2 line-clamp-3 text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
            {book.description || "暂无简介"}
          </p>
          {book.tags.length > 0 ? (
            <ul className="mt-2 flex flex-wrap gap-1.5">
              {book.tags.map((t) => (
                <li
                  key={t}
                  className="rounded-md bg-zinc-50 px-2 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800/80 dark:text-zinc-400"
                >
                  {t}
                </li>
              ))}
            </ul>
          ) : null}
          <p className="mt-3 text-xs text-zinc-500 dark:text-zinc-500">
            最新：
            {book.latest_chapter_title ? (
              <span className="text-zinc-700 dark:text-zinc-300">
                {book.latest_chapter_title}
              </span>
            ) : (
              "—"
            )}
            <span className="mx-2">·</span>
            更新 {formatTime(book.updated_at)}
          </p>
        </div>
      </div>
    </article>
  );
}
