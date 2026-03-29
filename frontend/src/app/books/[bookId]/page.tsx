import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { fetchBook } from "@/lib/api";
import { assetUrl } from "@/lib/env";

type Props = { params: Promise<{ bookId: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { bookId } = await params;
  const data = await fetchBook(bookId);
  if (!data) return { title: "未找到" };
  const { book } = data;
  return {
    title: book.title,
    description: book.description?.slice(0, 160) || book.title,
  };
}

export default async function BookDetailPage({ params }: Props) {
  const { bookId } = await params;
  const data = await fetchBook(bookId);
  if (!data) notFound();

  const { book, chapters } = data;
  const coverSrc = assetUrl(book.cover);
  const statusLabel = book.status === "completed" ? "完结" : "连载";

  return (
    <article>
      <div className="flex flex-col gap-6 sm:flex-row sm:items-start">
        <div className="relative mx-auto h-52 w-36 shrink-0 overflow-hidden rounded-lg bg-zinc-100 dark:bg-zinc-800 sm:mx-0">
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
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            {book.title}
          </h1>
          <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-zinc-600 dark:text-zinc-400">
            {book.author ? <span>{book.author}</span> : null}
            <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs dark:bg-zinc-800">
              {statusLabel}
            </span>
          </div>
          {book.tags.length > 0 ? (
            <ul className="mt-3 flex flex-wrap gap-1.5">
              {book.tags.map((t) => (
                <li
                  key={t}
                  className="rounded-md bg-zinc-100 px-2 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400"
                >
                  {t}
                </li>
              ))}
            </ul>
          ) : null}
          <p className="mt-4 text-base leading-relaxed text-zinc-700 dark:text-zinc-300">
            {book.description || "暂无简介"}
          </p>
        </div>
      </div>

      <section className="mt-12">
        <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">目录</h2>
        <ol className="mt-4 divide-y divide-zinc-200 rounded-lg border border-zinc-200 dark:divide-zinc-800 dark:border-zinc-800">
          {chapters.length === 0 ? (
            <li className="px-4 py-6 text-sm text-zinc-500">暂无章节</li>
          ) : (
            chapters.map((ch) => (
              <li key={ch.slug}>
                <Link
                  href={`/books/${book.id}/chapters/${ch.slug}`}
                  className="flex items-baseline justify-between gap-4 px-4 py-3 text-sm hover:bg-zinc-50 dark:hover:bg-zinc-900/50"
                >
                  <span className="text-zinc-500 tabular-nums">第 {ch.number} 章</span>
                  <span className="min-w-0 flex-1 font-medium text-zinc-900 dark:text-zinc-100">
                    {ch.title}
                  </span>
                </Link>
              </li>
            ))
          )}
        </ol>
      </section>
    </article>
  );
}
