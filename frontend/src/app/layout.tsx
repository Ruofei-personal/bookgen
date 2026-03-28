import type { Metadata } from "next";
import "./globals.css";
import { SiteHeader } from "@/components/SiteHeader";

/** Avoid prerender-time fetch to API (build / Docker 构建时后端未必可用). */
export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: {
    default: "书荒救星",
    template: "%s · 书荒救星",
  },
  description: "书荒救星：极简小说阅读与更新追更",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-zinc-50 antialiased dark:bg-zinc-950">
        <SiteHeader />
        <main className="mx-auto w-full max-w-5xl px-4 py-6 sm:px-6 sm:py-8">{children}</main>
      </body>
    </html>
  );
}
