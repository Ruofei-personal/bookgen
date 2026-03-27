#!/usr/bin/env bash
# 停止由 native-start.sh 记录在本仓库 .run/ 下的 API / 前端进程（仅针对 bookgen 脚本启动的实例）。
#
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN="$ROOT/.run"

stop_one() {
  local name="$1"
  local pidfile="$RUN/$2"
  if [ ! -f "$pidfile" ]; then
    return 0
  fi
  local pid
  pid="$(cat "$pidfile" 2>/dev/null || true)"
  if [ -z "${pid:-}" ]; then
    rm -f "$pidfile"
    return 0
  fi
  if kill -0 "$pid" 2>/dev/null; then
    echo "native-stop: stopping $name (pid $pid)"
    kill "$pid" 2>/dev/null || true
    sleep 1
    if kill -0 "$pid" 2>/dev/null; then
      kill -9 "$pid" 2>/dev/null || true
    fi
  fi
  rm -f "$pidfile"
}

mkdir -p "$RUN"
stop_one "API" "api.pid"
stop_one "frontend" "web.pid"
echo "native-stop: done."
