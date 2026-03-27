import Link from "next/link";

export default function NotFound() {
  return (
    <div className="py-16 text-center">
      <h1 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">页面不存在</h1>
      <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
        可能书籍或章节尚未发布，或链接有误。
      </p>
      <Link href="/" className="mt-6 inline-block text-sm text-zinc-700 underline dark:text-zinc-300">
        返回首页
      </Link>
    </div>
  );
}
