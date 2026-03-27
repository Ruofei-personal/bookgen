#!/usr/bin/env bash
# 本地开发：并行启动后端 API 与 Next.js 前端（同一终端，Ctrl+C 一并结束）。
#
# 后端：  cd backend && uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
# 前端：  cd frontend && npm run dev   （默认端口 8765，见 frontend/package.json）
#
# 首次请先：backend 执行 uv sync；frontend 执行 npm ci。
#
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "bookgen dev: API :8001 + Next :8765 (Ctrl+C stops both)"
trap 'kill 0' INT TERM
(
  cd "$ROOT/backend"
  uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
) &
(
  cd "$ROOT/frontend"
  npm run dev
) &
wait
