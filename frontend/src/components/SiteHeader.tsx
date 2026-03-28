import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-20 border-b border-zinc-200/80 bg-white/85 backdrop-blur-md dark:border-zinc-800 dark:bg-zinc-950/85">
      <div className="mx-auto flex w-full max-w-5xl items-center justify-between gap-4 px-4 py-3 sm:px-6 sm:py-4">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-base font-semibold tracking-tight text-zinc-900 transition hover:text-zinc-700 dark:text-zinc-50 dark:hover:text-zinc-200 sm:text-lg"
        >
          <span className="inline-flex h-7 w-7 items-center justify-center rounded-lg bg-zinc-900 text-sm text-white dark:bg-zinc-100 dark:text-zinc-900">
            书
          </span>
          书荒救星
        </Link>
        <nav className="rounded-full border border-zinc-200/80 bg-white/70 px-3 py-1 text-sm text-zinc-600 dark:border-zinc-800 dark:bg-zinc-900/70 dark:text-zinc-300">
          <Link href="/" className="transition hover:text-zinc-900 dark:hover:text-zinc-100">
            首页
          </Link>
        </nav>
      </div>
    </header>
  );
}
