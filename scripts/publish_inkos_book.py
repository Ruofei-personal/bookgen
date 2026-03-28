#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


def run(cmd: list[str], cwd: Path) -> None:
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=str(cwd), check=True)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def find_cover_file(target_dir: Path) -> Path | None:
    assets = target_dir / "assets"
    if not assets.is_dir():
        return None
    for ext in ("png", "jpg", "jpeg", "webp"):
        candidate = assets / f"cover.{ext}"
        if candidate.is_file():
            return candidate
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish an InkOS book into bookgen with safer defaults")
    parser.add_argument("--repo", default="/home/ruofei/bookgen", help="Path to bookgen repo")
    parser.add_argument("--inkos-book", required=True, help="Path to InkOS book directory")
    parser.add_argument("--book-id", required=True, help="Target book id in content/books")
    parser.add_argument("--title", help="Public title")
    parser.add_argument("--author", help="Public author")
    parser.add_argument("--description", help="Public description")
    parser.add_argument("--description-file", help="Read public description from a UTF-8 text file")
    parser.add_argument("--tags", nargs="*", default=None, help="Public tags")
    parser.add_argument("--cover", help="Path to cover image file to copy into assets/cover.*")
    parser.add_argument("--status", default="ongoing", choices=["ongoing", "completed"], help="Book status")
    parser.add_argument("--commit-message", default="Publish InkOS book update", help="Git commit message")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    inkos_book = Path(args.inkos_book).resolve()
    target_dir = repo / "content" / "books" / args.book_id
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "assets").mkdir(parents=True, exist_ok=True)

    existing_cover = find_cover_file(target_dir)

    run([
        "python3",
        "scripts/import_inkos_book.py",
        "--inkos-book", str(inkos_book),
        "--content-root", str(repo / "content" / "books"),
        "--book-id", args.book_id,
        "--chapters-only",
    ], repo)

    book_json_path = target_dir / "book.json"
    book_json = read_json(book_json_path) if book_json_path.is_file() else {}

    if args.title:
        book_json["title"] = args.title
    if args.author:
        book_json["author"] = args.author

    description_value = None
    if args.description_file:
        description_value = Path(args.description_file).resolve().read_text(encoding="utf-8").strip()
    elif args.description:
        description_value = args.description
    if description_value is not None:
        book_json["description"] = description_value

    if args.tags is not None:
        book_json["tags"] = args.tags
    if args.status:
        book_json["status"] = args.status

    if args.cover:
        src = Path(args.cover).resolve()
        if not src.is_file():
            raise SystemExit(f"Cover file not found: {src}")
        ext = src.suffix.lower() or ".png"
        dest = target_dir / "assets" / f"cover{ext}"
        # remove old cover variants
        for old in (target_dir / "assets").glob("cover.*"):
            old.unlink(missing_ok=True)
        dest.write_bytes(src.read_bytes())
        book_json["cover"] = f"/content/books/{args.book_id}/assets/{dest.name}"
    elif existing_cover:
        book_json["cover"] = f"/content/books/{args.book_id}/assets/{existing_cover.name}"

    write_json(book_json_path, book_json)

    run(["./scripts/deploy.sh"], repo)
    run(["./scripts/check.sh"], repo)
    run(["git", "add", f"content/books/{args.book_id}", "scripts/import_inkos_book.py", "scripts/publish_inkos_book.py"], repo)
    run(["git", "commit", "-m", args.commit_message], repo)
    run(["git", "push"], repo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
