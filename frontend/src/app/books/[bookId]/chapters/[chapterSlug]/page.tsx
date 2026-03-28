import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { ArticleBody } from "@/components/ArticleBody";
import { ChapterNav } from "@/components/ChapterNav";
import { fetchBook, fetchChapter } from "@/lib/api";

type Props = { params: Promise<{ bookId: string; chapterSlug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { bookId, chapterSlug } = await params;
  const [bookData, chData] = await Promise.all([
    fetchBook(bookId),
    fetchChapter(bookId, chapterSlug),
  ]);
  if (!bookData || !chData) return { title: "未找到" };
  const title = chData.chapter.meta.title;
  return {
    title: `${bookData.book.title} · ${title}`,
    description: chData.chapter.meta.summary || title,
  };
}

export default async function ChapterPage({ params }: Props) {
  const { bookId, chapterSlug } = await params;
  const data = await fetchChapter(bookId, chapterSlug);
  if (!data) notFound();

  const { chapter, prev, next } = data;

  return (
    <article>
      <header className="mb-8 border-b border-zinc-200 pb-6 dark:border-zinc-800">
        <p className="text-sm text-zinc-500">第 {chapter.meta.number} 章</p>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
          {chapter.meta.title}
        </h1>
        {chapter.meta.summary ? (
          <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">{chapter.meta.summary}</p>
        ) : null}
        {chapter.meta.audio ? (
          <div className="mt-4">
            <audio controls preload="none" className="w-full">
              <source src={chapter.meta.audio} type="audio/mpeg" />
              您的浏览器暂不支持音频播放。
            </audio>
          </div>
        ) : null}
      </header>

      <ArticleBody html={chapter.content_html} />

      <ChapterNav bookId={bookId} prev={prev} next={next} />
    </article>
  );
}
