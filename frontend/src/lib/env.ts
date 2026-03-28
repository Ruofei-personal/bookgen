/** Server-side API base (FastAPI). No NEXT_PUBLIC_ required for RSC fetches. */
export function getApiBase(): string {
  return (
    process.env.API_URL?.replace(/\/$/, "") ||
    process.env.BACKEND_URL?.replace(/\/$/, "") ||
    "http://127.0.0.1:8001"
  );
}

/** URL for static assets and images served by the API (e.g. /content/...).
 * These assets live on the FastAPI service, not the Next.js frontend server.
 * Use API_BASE for root-relative content paths so external browsers don't hit
 * localhost while still reaching the correct host/port.
 */
export function assetUrl(path: string | null | undefined): string | null {
  if (!path) return null;
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  const normalized = path.startsWith("/") ? path : `/${path}`;
  if (normalized.startsWith("/content/")) return `${getApiBase()}${normalized}`;
  return normalized;
}
