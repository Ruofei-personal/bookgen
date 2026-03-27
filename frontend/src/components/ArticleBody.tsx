/** Renders server-sanitized HTML from the API (nh3 + markdown). */
export function ArticleBody({ html }: { html: string }) {
  return (
    <div
      className="novel-prose"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
