#!/usr/bin/env bash
# 部署后健康检查：失败时非零退出。API / 前端均带重试，避免 Next 刚启动前几秒误判。
#
# 环境变量：
#   API_URL              后端根 URL，默认 http://127.0.0.1:8001
#   FRONTEND_URL         前端根 URL，默认 http://127.0.0.1:8765
#   CHECK_MAX_ATTEMPTS   每种检查的最大尝试次数，默认 30
#   CHECK_INTERVAL_SEC   两次尝试间隔（秒），默认 2（合计约 1 分钟量级）
#
set -uo pipefail

API_URL="${API_URL:-http://127.0.0.1:8001}"
FRONTEND_URL="${FRONTEND_URL:-http://127.0.0.1:8765}"
MAX_ATTEMPTS="${CHECK_MAX_ATTEMPTS:-30}"
INTERVAL="${CHECK_INTERVAL_SEC:-2}"

API_URL="${API_URL%/}"
FRONTEND_URL="${FRONTEND_URL%/}"

echo "check.sh: API=$API_URL FRONTEND=$FRONTEND_URL (up to ${MAX_ATTEMPTS} tries × ${INTERVAL}s apart)"

try_api_once() {
  curl -sfS --max-time 10 "${API_URL}/api/health" >/dev/null
}

try_frontend_once() {
  local code
  code="$(curl -sS -L --max-time 10 -o /dev/null -w '%{http_code}' "${FRONTEND_URL}/" 2>/dev/null || echo "000")"
  [ "$code" = "200" ]
}

wait_for() {
  local name="$1"
  shift
  local attempt=1
  while [ "$attempt" -le "$MAX_ATTEMPTS" ]; do
    if "$@"; then
      echo "check.sh: ${name} OK (attempt ${attempt}/${MAX_ATTEMPTS})"
      return 0
    fi
    echo "check.sh: ${name} not ready (attempt ${attempt}/${MAX_ATTEMPTS}), waiting ${INTERVAL}s..." >&2
    sleep "$INTERVAL"
    attempt=$((attempt + 1))
  done
  echo "check.sh: ${name} FAILED after ${MAX_ATTEMPTS} attempts" >&2
  return 1
}

if ! wait_for "API health" try_api_once; then
  echo "check.sh: overall FAILED (API)." >&2
  exit 1
fi

if ! wait_for "frontend home" try_frontend_once; then
  echo "check.sh: overall FAILED (frontend)." >&2
  exit 1
fi

echo "check.sh: all checks passed."
exit 0
