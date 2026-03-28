#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN="$ROOT/.run"

show_proc() {
  local name="$1"
  local pidfile="$2"
  local pid=""
  if [ -f "$pidfile" ]; then
    pid="$(cat "$pidfile" 2>/dev/null || true)"
  fi
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    echo "$name: running (pid $pid)"
    ps -o pid,ppid,etime,stat,cmd -p "$pid"
  else
    echo "$name: not running"
  fi
}

echo "== bookgen native status =="
show_proc "API" "$RUN/api.pid"
echo
show_proc "Frontend" "$RUN/web.pid"
echo
if [ -f "$RUN/last-start.json" ]; then
  echo "== last-start.json =="
  cat "$RUN/last-start.json"
fi
