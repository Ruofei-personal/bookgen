/** Server-side API base (FastAPI). No NEXT_PUBLIC_ required for RSC fetches. */
export function getApiBase(): string {
  return (
    process.env.API_URL?.replace(/\/$/, "") ||
    process.env.BACKEND_URL?.replace(/\/$/, "") ||
    "http://127.0.0.1:8001"
  );
}

/** URL for static assets and images served by the API (e.g. /content/...).
 * In the current native deployment, /content is served by FastAPI on the API
 * host/port instead of the Next.js frontend port, so content paths must be
 * expanded against API_BASE.
 */
export function assetUrl(path: string | null | undefined): string | null {
  if (!path) return null;
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  const normalized = path.startsWith("/") ? path : `/${path}`;
  if (normalized.startsWith("/content/")) return `${getApiBase()}${normalized}`;
  return normalized;
}
