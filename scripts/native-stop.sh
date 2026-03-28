#!/usr/bin/env bash
# 停止由 native-start.sh 记录在本仓库 .run/ 下的 API / 前端进程。
# 同时兜底清理仍占用 8001/8765 的 bookgen 相关残留进程，避免端口被旧实例卡住。
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

kill_port_holders() {
  local port="$1"
  local label="$2"
  local pids
  pids="$(ss -tlnp 2>/dev/null | awk -v p=":$port" '$4 ~ p {print $NF}' | grep -o 'pid=[0-9]\+' | cut -d= -f2 | sort -u || true)"
  if [ -z "$pids" ]; then
    return 0
  fi
  for pid in $pids; do
    if [ -r "/proc/$pid/cwd" ]; then
      local cwd
      cwd="$(readlink -f "/proc/$pid/cwd" 2>/dev/null || true)"
      if [[ "$cwd" == "$ROOT"/* || "$cwd" == "$ROOT" ]]; then
        echo "native-stop: killing leftover $label listener on :$port (pid $pid, cwd $cwd)"
        kill -9 "$pid" 2>/dev/null || true
      fi
    fi
  done
}

mkdir -p "$RUN"
stop_one "API" "api.pid"
stop_one "frontend" "web.pid"
systemctl --user stop bookgen-api.service 2>/dev/null || true
systemctl --user stop bookgen-web.service 2>/dev/null || true
kill_port_holders 8001 "API"
kill_port_holders 8765 "frontend"
echo "native-stop: done."
