import type { Metadata } from "next";
import "./globals.css";
import { SiteHeader } from "@/components/SiteHeader";

/** Avoid prerender-time fetch to API (build / Docker 构建时后端未必可用). */
export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: {
    default: "bookgen",
    template: "%s · bookgen",
  },
  description: "极简小说阅读与发布",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen antialiased">
        <SiteHeader />
        <main className="mx-auto max-w-3xl px-4 py-8 sm:px-6 sm:py-10">{children}</main>
      </body>
    </html>
  );
}
