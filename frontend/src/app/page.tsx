import type { Metadata } from "next";
import { BookCard } from "@/components/BookCard";
import { fetchBooks } from "@/lib/api";

export const metadata: Metadata = {
  title: "首页",
  description: "书荒救星 · 公开小说书库",
};

export default async function HomePage() {
  const { books } = await fetchBooks();

  return (
    <div className="space-y-8 sm:space-y-10">
      <section className="rounded-2xl border border-zinc-200/80 bg-gradient-to-br from-amber-50 via-white to-orange-50 p-5 shadow-sm dark:border-zinc-800 dark:from-zinc-900 dark:via-zinc-950 dark:to-zinc-900/80 sm:p-8">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-amber-700 dark:text-amber-300">
          书荒救星
        </p>
        <h1 className="mt-3 text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50 sm:text-3xl">
          发现下一本让你停不下来的小说
        </h1>
        <p className="mt-3 max-w-2xl text-sm leading-relaxed text-zinc-600 dark:text-zinc-400 sm:text-base">
          精选书目按更新时间排序，打开即读，支持电脑与手机顺畅浏览。无论是短暂摸鱼还是长时间沉浸，都能快速找到合口味的故事。
        </p>
        <div className="mt-5 flex flex-wrap gap-2">
          <span className="rounded-full bg-white/80 px-3 py-1 text-xs text-zinc-700 ring-1 ring-zinc-200 dark:bg-zinc-900/70 dark:text-zinc-300 dark:ring-zinc-700">
            {books.length} 本在库作品
          </span>
          <span className="rounded-full bg-white/80 px-3 py-1 text-xs text-zinc-700 ring-1 ring-zinc-200 dark:bg-zinc-900/70 dark:text-zinc-300 dark:ring-zinc-700">
            实时更新书单
          </span>
          <span className="rounded-full bg-white/80 px-3 py-1 text-xs text-zinc-700 ring-1 ring-zinc-200 dark:bg-zinc-900/70 dark:text-zinc-300 dark:ring-zinc-700">
            移动端友好阅读
          </span>
        </div>
      </section>

      <section>
        <div className="mb-4 flex items-end justify-between gap-3">
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 sm:text-xl">最新书目</h2>
          <p className="text-xs text-zinc-500 dark:text-zinc-400">按最近更新时间展示</p>
        </div>

        <ul className="grid grid-cols-1 gap-4 sm:gap-5">
          {books.length === 0 ? (
            <li className="rounded-xl border border-dashed border-zinc-300 bg-white p-8 text-center text-sm text-zinc-500 dark:border-zinc-700 dark:bg-zinc-900/50 dark:text-zinc-400">
              暂无书籍，请稍后再来看看。
            </li>
          ) : (
            books.map((book) => (
              <li key={book.id}>
                <BookCard book={book} />
              </li>
            ))
          )}
        </ul>
      </section>
    </div>
  );
}
