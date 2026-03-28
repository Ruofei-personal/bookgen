import Link from "next/link";
import type { NavChapter } from "@/lib/types";

export function ChapterNav({
  bookId,
  prev,
  next,
}: {
  bookId: string;
  prev: NavChapter | null;
  next: NavChapter | null;
}) {
  const base = `/books/${bookId}`;
  return (
    <nav className="mt-10 grid grid-cols-3 items-center gap-3 border-t border-zinc-200 pt-8 text-sm dark:border-zinc-800">
      <div className="min-h-[1.5rem] text-left">
        {prev ? (
          <Link
            href={`${base}/chapters/${prev.slug}`}
            className="inline-block max-w-full truncate text-zinc-700 hover:underline dark:text-zinc-300"
            title={`上一章：${prev.title}`}
          >
            ← 上一章：{prev.title}
          </Link>
        ) : (
          <span className="text-zinc-400">← 没有上一章</span>
        )}
      </div>
      <Link
        href={base}
        className="text-center text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-200"
      >
        返回目录
      </Link>
      <div className="min-h-[1.5rem] text-right">
        {next ? (
          <Link
            href={`${base}/chapters/${next.slug}`}
            className="inline-block max-w-full truncate text-zinc-700 hover:underline dark:text-zinc-300"
            title={`下一章：${next.title}`}
          >
            下一章：{next.title} →
          </Link>
        ) : (
          <span className="text-zinc-400">没有下一章 →</span>
        )}
      </div>
    </nav>
  );
}
