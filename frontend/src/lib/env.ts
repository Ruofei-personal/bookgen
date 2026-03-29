/** Server-side API base (FastAPI). No NEXT_PUBLIC_ required for RSC fetches. */
export function getApiBase(): string {
  return (
    process.env.API_URL?.replace(/\/$/, "") ||
    process.env.BACKEND_URL?.replace(/\/$/, "") ||
    "http://127.0.0.1:8001"
  );
}

/** URL for static assets and images.
 * /content paths are expected to be served as same-origin routes by Next.js
 * rewrites, so keep them relative for browser playback/caching compatibility.
 */
export function assetUrl(path: string | null | undefined): string | null {
  if (!path) return null;
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  const normalized = path.startsWith("/") ? path : `/${path}`;
  if (normalized.startsWith("/content/")) return normalized;
  return normalized;
}
