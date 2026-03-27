import type { Metadata } from "next";
import { BookCard } from "@/components/BookCard";
import { fetchBooks } from "@/lib/api";

export const metadata: Metadata = {
  title: "首页",
  description: "公开小说列表",
};

export default async function HomePage() {
  const { books } = await fetchBooks();

  return (
    <div>
      <p className="text-sm font-medium uppercase tracking-widest text-zinc-500 dark:text-zinc-400">
        bookgen
      </p>
      <h1 className="mt-2 text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
        小说列表
      </h1>
      <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
        文件驱动，便于脚本与自动化发布。
      </p>
      <ul className="mt-8 flex flex-col gap-6">
        {books.length === 0 ? (
          <li className="rounded-lg border border-dashed border-zinc-300 p-8 text-center text-sm text-zinc-500 dark:border-zinc-700">
            暂无书籍。请在后端 content 目录下添加书目与章节。
          </li>
        ) : (
          books.map((book) => (
            <li key={book.id}>
              <BookCard book={book} />
            </li>
          ))
        )}
      </ul>
    </div>
  );
}
