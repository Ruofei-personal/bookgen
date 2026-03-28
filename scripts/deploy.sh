#!/usr/bin/env bash
# 生产/准生产部署入口：可重复执行（幂等）。
#
# 环境变量：
#   BOOKGEN_DEPLOY_MODE          auto（默认）| docker | native
#                                auto：Docker daemon 可用则用 compose，否则 native
#   BOOKGEN_NATIVE_RESTART_CMD   native 下若设置，则构建后执行该命令（如 systemctl），不跑 native-start
#   BOOKGEN_NATIVE_AUTOSTART     native 下是否自动后台启动（默认 1）。设为 0 则只构建，由你自管进程
#
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

have_docker_cli() {
  command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1
}

docker_daemon_ok() {
  docker info >/dev/null 2>&1
}

docker_usable() {
  have_docker_cli && docker_daemon_ok
}

mode="${BOOKGEN_DEPLOY_MODE:-auto}"
if [ "$mode" = "auto" ]; then
  if docker_usable; then
    mode=docker
  elif have_docker_cli && ! docker_daemon_ok; then
    echo "bookgen deploy: [auto] Docker 已安装但无法连接 daemon（常见：当前用户无权访问 Docker socket）。" >&2
    echo "bookgen deploy: [auto] 将改用 native。若需 Docker：sudo usermod -aG docker \"\$USER\" 后重新登录，或 sudo docker compose ..." >&2
    mode=native
  else
    mode=native
  fi
fi

if [ "$mode" = "docker" ] && ! docker_usable; then
  echo "bookgen deploy: ERROR: 已指定 BOOKGEN_DEPLOY_MODE=docker，但 Docker 不可用（未安装、daemon 未启动或无权限）。" >&2
  echo "bookgen deploy: ERROR: 请改用: BOOKGEN_DEPLOY_MODE=native ./scripts/deploy.sh" >&2
  exit 1
fi

echo "bookgen deploy: ────────────────────────────────"
echo "bookgen deploy: 使用模式: $mode"
echo "bookgen deploy: 仓库路径: $ROOT"
echo "bookgen deploy: ────────────────────────────────"

(
  cd "$ROOT/backend"
  uv sync --frozen
)

if [ "$mode" = "docker" ]; then
  echo "bookgen deploy: [docker] build + up -d..."
  docker compose -f "$ROOT/docker-compose.yml" build
  docker compose -f "$ROOT/docker-compose.yml" up -d --remove-orphans
  echo "bookgen deploy: [docker] 完成。宿主机端口: API :8001, Web :8765"
  echo "bookgen deploy: 建议下一步: ./scripts/check.sh"
  exit 0
fi

echo "bookgen deploy: [native] 构建 frontend + 校验 backend venv..."
"$ROOT/scripts/build.sh"

echo "bookgen deploy: [native] 清理旧进程并准备干净重启..."
"$ROOT/scripts/native-stop.sh"

if [ -n "${BOOKGEN_NATIVE_RESTART_CMD:-}" ]; then
  echo "bookgen deploy: [native] 执行 BOOKGEN_NATIVE_RESTART_CMD..."
  bash -c "$BOOKGEN_NATIVE_RESTART_CMD"
  echo "bookgen deploy: [native] 完成。"
elif [ "${BOOKGEN_NATIVE_AUTOSTART:-1}" != "0" ]; then
  echo "bookgen deploy: [native] 后台启动 API + Next（native-start.sh）..."
  "$ROOT/scripts/native-start.sh"
else
  echo "bookgen deploy: [native] 已跳过自动启动（BOOKGEN_NATIVE_AUTOSTART=0）。请自行启动，例如：" >&2
  echo "  cd $ROOT/backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8001" >&2
  echo "  cd $ROOT/frontend && API_URL=http://127.0.0.1:8001 npm run start" >&2
  echo "bookgen deploy: 或使用: ./scripts/native-start.sh" >&2
fi

echo "bookgen deploy: 建议下一步: ./scripts/check.sh（含重试，可等待前端就绪）"
exit 0
