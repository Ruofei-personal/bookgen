#!/usr/bin/env bash
# Native 部署：在宿主机后台启动 API（:8001）与 Next 生产进程（:8765），日志与 PID 写在 .run/。
# 部署前请先在同一仓库执行 ./scripts/build.sh（或由 deploy.sh 调用）。
#
# 环境变量：
#   API_URL  传给前端的基地址（默认 http://127.0.0.1:8001），与 frontend/.env.local 一致即可
#
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN="$ROOT/.run"
mkdir -p "$RUN"

export API_URL="${API_URL:-http://127.0.0.1:8001}"

echo "native-start: repo=$ROOT"
echo "native-start: stopping previous bookgen native processes (if any)..."
"$ROOT/scripts/native-stop.sh"

echo "native-start: starting API on :8001 (log $RUN/api.log)"
cd "$ROOT/backend"
nohup uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 >>"$RUN/api.log" 2>&1 &
echo $! >"$RUN/api.pid"

echo "native-start: starting Next on :8765 (log $RUN/web.log), API_URL=$API_URL"
cd "$ROOT/frontend"
nohup env API_URL="$API_URL" npm run start >>"$RUN/web.log" 2>&1 &
echo $! >"$RUN/web.pid"

echo "native-start: PIDs api=$(cat "$RUN/api.pid") web=$(cat "$RUN/web.pid")"
echo "native-start: Next.js 首次监听可能需要十余秒，请用 ./scripts/check.sh 验证（内置重试）。"
