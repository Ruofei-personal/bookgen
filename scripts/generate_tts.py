#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import re
from pathlib import Path

try:
    import edge_tts
except ImportError as exc:  # pragma: no cover - runtime guidance only
    raise SystemExit(
        "缺少 edge-tts 依赖，请先在 backend 目录执行 `uv sync`。"
    ) from exc

DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"
REPO_ROOT = Path(__file__).resolve().parents[1]
BOOKS_ROOT = REPO_ROOT / "content" / "books"


def _chapter_token(chapter_value: str) -> str:
    token = chapter_value.strip()
    if not token.isdigit():
        raise ValueError(f"章节号必须是数字，收到: {chapter_value}")
    return f"{int(token):03d}"


def markdown_to_tts_text(markdown_text: str, *, keep_heading: bool = True) -> str:
    text = markdown_text.replace("\r\n", "\n")
    text = re.sub(r"```[\s\S]*?```", "\n", text)
    text = re.sub(r"`[^`]*`", "", text)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]*)\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]*)\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"^\s{0,3}([-*_])\1{2,}\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*>\s?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)

    def _heading_repl(match: re.Match[str]) -> str:
        heading = match.group(2).strip()
        return f"{heading}\n" if keep_heading and heading else ""

    text = re.sub(r"^(#{1,6})\s*(.+)$", _heading_repl, text, flags=re.MULTILINE)
    text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)
    text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)
    text = re.sub(r"~~(.*?)~~", r"\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


async def _synthesize(text: str, target_file: Path, voice: str) -> None:
    target_file.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(str(target_file))


def _update_meta_audio(meta_path: Path, audio_url: str) -> None:
    data = json.loads(meta_path.read_text(encoding="utf-8"))
    if data.get("audio") == audio_url:
        return
    data["audio"] = audio_url
    meta_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _resolve_targets(book_dir: Path, chapter: str | None, all_chapters: bool) -> list[str]:
    if all_chapters:
        chapter_files = sorted((book_dir / "chapters").glob("*.md"))
        return [file.stem for file in chapter_files if file.stem.isdigit()]
    if chapter is None:
        raise ValueError("必须提供 --chapter 或 --all")
    return [_chapter_token(chapter)]


def _generate_for_one(book_id: str, chapter_token: str, voice: str, overwrite: bool) -> None:
    book_dir = BOOKS_ROOT / book_id
    md_path = book_dir / "chapters" / f"{chapter_token}.md"
    meta_path = book_dir / "meta" / f"{chapter_token}.json"
    audio_path = book_dir / "audio" / f"{chapter_token}.mp3"
    audio_url = f"/content/books/{book_id}/audio/{chapter_token}.mp3"

    if not md_path.is_file():
        raise FileNotFoundError(f"未找到章节正文: {md_path}")
    if not meta_path.is_file():
        raise FileNotFoundError(f"未找到章节 meta: {meta_path}")
    if audio_path.exists() and not overwrite:
        print(f"[skip] {chapter_token} 已存在音频（使用 --overwrite 可覆盖）")
        _update_meta_audio(meta_path, audio_url)
        return

    markdown_text = md_path.read_text(encoding="utf-8")
    tts_text = markdown_to_tts_text(markdown_text)
    if not tts_text:
        raise ValueError(f"章节 {chapter_token} 清洗后为空，停止生成。")

    print(f"[tts] 生成 {book_id}/{chapter_token} -> {audio_path}")
    asyncio.run(_synthesize(tts_text, audio_path, voice))
    _update_meta_audio(meta_path, audio_url)
    print(f"[ok] 已写入音频与 meta: {audio_url}")


def main() -> None:
    parser = argparse.ArgumentParser(description="为章节预生成 edge-tts 音频。")
    parser.add_argument("--book-id", required=True, help="书籍 ID（content/books/<book-id>）")
    parser.add_argument("--chapter", help="单章号，如 1 或 001")
    parser.add_argument("--all", action="store_true", help="整本生成")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help=f"edge-tts 音色，默认 {DEFAULT_VOICE}")
    parser.add_argument("--overwrite", action="store_true", help="覆盖已存在 mp3")
    args = parser.parse_args()

    if args.all and args.chapter:
        raise SystemExit("--all 与 --chapter 只能二选一。")

    book_dir = BOOKS_ROOT / args.book_id
    if not book_dir.is_dir():
        raise SystemExit(f"书籍不存在: {book_dir}")

    targets = _resolve_targets(book_dir, args.chapter, args.all)
    if not targets:
        raise SystemExit("没有找到可生成的章节。")

    for chapter_token in targets:
        _generate_for_one(args.book_id, chapter_token, args.voice, args.overwrite)


if __name__ == "__main__":
    main()
