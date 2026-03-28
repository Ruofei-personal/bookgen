/** Server-side API base (FastAPI). No NEXT_PUBLIC_ required for RSC fetches. */
export function getApiBase(): string {
  return (
    process.env.API_URL?.replace(/\/$/, "") ||
    process.env.BACKEND_URL?.replace(/\/$/, "") ||
    "http://127.0.0.1:8001"
  );
}

/** URL for static assets and images served by the API (e.g. /content/...).
 * Prefer root-relative paths in rendered HTML so external browsers do not see
 * server-local origins like 127.0.0.1.
 */
export function assetUrl(path: string | null | undefined): string | null {
  if (!path) return null;
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  const normalized = path.startsWith("/") ? path : `/${path}`;
  if (normalized.startsWith("/content/")) return normalized;
  return normalized;
}
