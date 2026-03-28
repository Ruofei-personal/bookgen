#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff\-\s]+", "", value)
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "book"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def chapter_num_from_name(path: Path) -> int | None:
    m = re.search(r"(\d+)", path.stem)
    return int(m.group(1)) if m else None


def discover_chapters(inkos_book_dir: Path) -> list[dict[str, Any]]:
    chapters_dir = inkos_book_dir / "chapters"
    if not chapters_dir.is_dir():
        return []

    discovered: list[dict[str, Any]] = []
    for path in sorted(chapters_dir.iterdir()):
        if not path.is_file():
            continue
        if path.name == "index.json":
            continue
        if path.suffix.lower() not in {".md", ".txt"}:
            continue

        number = chapter_num_from_name(path)
        if number is None:
            continue

        text = read_text(path).strip()
        title = f"第{number}章"
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if lines and (lines[0].startswith("#") or len(lines[0]) <= 40):
            first = lines[0].lstrip("#").strip()
            if first:
                title = first
                body = "\n".join(text.splitlines()[1:]).strip()
                text = body or text

        discovered.append({
            "number": number,
            "title": title,
            "content": text,
        })

    discovered.sort(key=lambda x: x["number"])
    return discovered


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import an InkOS book into bookgen content/books format")
    parser.add_argument("--inkos-book", required=True, help="Path to InkOS book directory")
    parser.add_argument("--content-root", default="content/books", help="Target content/books root")
    parser.add_argument("--book-id", help="Target book id (defaults to slugified InkOS title)")
    parser.add_argument("--title", help="Override book title")
    parser.add_argument("--author", default="InkOS / Jeff", help="Book author")
    parser.add_argument("--description", help="Override description")
    parser.add_argument("--status", default="ongoing", choices=["ongoing", "completed"], help="Book status")
    parser.add_argument("--tags", nargs="*", default=[], help="Book tags")
    parser.add_argument("--replace", action="store_true", help="Replace target book directory before import")
    return parser.parse_args()


def build_description(inkos_book_dir: Path, override: str | None) -> str:
    if override:
        return override
    candidates = [
        inkos_book_dir / "story" / "author_intent.md",
        inkos_book_dir / "story" / "current_focus.md",
        inkos_book_dir / "story" / "story_bible.md",
    ]
    for path in candidates:
        if path.is_file():
            text = read_text(path).strip()
            text = re.sub(r"#+\s*", "", text)
            text = re.sub(r"\n{2,}", "\n", text)
            if text:
                return text[:500]
    return "Imported from InkOS."


def main() -> int:
    args = parse_args()
    inkos_book_dir = Path(args.inkos_book).resolve()
    if not inkos_book_dir.is_dir():
        raise SystemExit(f"InkOS book dir not found: {inkos_book_dir}")

    book_info_path = inkos_book_dir / "book.json"
    if not book_info_path.is_file():
        raise SystemExit(f"InkOS book.json not found: {book_info_path}")

    book_info = read_json(book_info_path)
    title = args.title or book_info.get("title") or inkos_book_dir.name
    book_id = args.book_id or slugify(str(title))
    content_root = Path(args.content_root).resolve()
    target_dir = content_root / book_id

    chapters = discover_chapters(inkos_book_dir)
    if not chapters:
        raise SystemExit(f"No chapter files found under: {inkos_book_dir / 'chapters'}")

    if target_dir.exists() and args.replace:
        shutil.rmtree(target_dir)

    (target_dir / "chapters").mkdir(parents=True, exist_ok=True)
    (target_dir / "meta").mkdir(parents=True, exist_ok=True)
    (target_dir / "assets").mkdir(parents=True, exist_ok=True)

    timestamp = now_iso()
    description = build_description(inkos_book_dir, args.description)

    latest = chapters[-1]
    book_json = {
        "id": book_id,
        "title": title,
        "author": args.author,
        "description": description,
        "status": args.status,
        "tags": args.tags,
        "cover": None,
        "created_at": book_info.get("createdAt") or timestamp,
        "updated_at": timestamp,
        "latest_chapter_title": latest["title"],
        "latest_chapter_number": latest["number"],
    }
    write_json(target_dir / "book.json", book_json)

    for chapter in chapters:
        number = int(chapter["number"])
        padded = f"{number:03d}"
        slug = f"chapter-{padded}"
        chapter_path = target_dir / "chapters" / f"{padded}.md"
        meta_path = target_dir / "meta" / f"{padded}.json"
        chapter_path.write_text(chapter["content"].rstrip() + "\n", encoding="utf-8")
        meta = {
            "id": slug,
            "book_id": book_id,
            "number": number,
            "title": chapter["title"],
            "slug": slug,
            "created_at": timestamp,
            "updated_at": timestamp,
            "summary": None,
        }
        write_json(meta_path, meta)

    print(json.dumps({
        "ok": True,
        "inkos_book": str(inkos_book_dir),
        "target_dir": str(target_dir),
        "book_id": book_id,
        "title": title,
        "chapters": len(chapters),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
