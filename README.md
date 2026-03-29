# bookgen

基于 **Python + FastAPI + uv** 与 **Next.js** 的极简小说发布站：内容以仓库根目录下的 `content/` 文件为主，无登录、无评论、无后台 CMS。详细需求见 [`novel-site-spec.md`](novel-site-spec.md)。

## 仓库结构

| 路径 | 说明 |
|------|------|
| `backend/` | FastAPI，读取 `content/books` 下的书目与章节 |
| `frontend/` | Next.js 站点（首页、书目、章节阅读） |
| `content/books/<book-id>/` | 每本书一个目录，见下文「内容目录」 |
| `scripts/` | `dev.sh` / `build.sh` / `deploy.sh` / `check.sh` / `native-start.sh` / `native-stop.sh` |
| `docker-compose.yml` | 生产推荐：统一拉起 API + 前端 |

## 环境要求

- Python **3.11+**、[uv](https://docs.astral.sh/uv/)
- Node.js **20+**、npm

## 后端（uv）

在 `backend/` 目录：

```bash
cd backend
uv sync
```

依赖由 `pyproject.toml` 与 `uv.lock` 锁定；不要用 `requirements.txt` 作为主依赖来源。

开发启动（默认读仓库根目录 `content/books`，可通过环境变量覆盖）：

```bash
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

生产示例：

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001
```

健康检查与 API 前缀：`GET http://127.0.0.1:8001/api/health`

## 前端（Next.js）

```bash
cd frontend
npm ci
npm run dev
```

默认开发端口 **8765**。生产构建与启动：

```bash
npm run build
npm run start
```

服务端请求后端的地址由环境变量 **`API_URL`**（或 `BACKEND_URL`）指定；本地可与根目录 `.env.example` 对照，在 `frontend/.env.local` 中设置，例如：

```bash
API_URL=http://127.0.0.1:8001
```

## 一键本地开发

在仓库根目录：

```bash
./scripts/dev.sh
```

会并行启动 API `:8001` 与 Next `:8765`。

## 构建

```bash
./scripts/build.sh
```

会执行 `backend` 的 `uv sync --frozen` 与 `frontend` 的 `npm ci`、`npm run build`（用于本机进程部署或 CI；Docker 部署会在镜像构建时再次执行等价步骤）。

## 部署与健康检查（脚本化 / OpenClaw）

目标：在服务器上稳定执行：

```bash
git pull
cd backend && uv sync && cd ..
./scripts/deploy.sh
./scripts/check.sh
```

`deploy.sh` 会打印当前是 **docker** 还是 **native**；`check.sh` 对 **API 与首页分别重试**（默认最多约 30 次、间隔 2 秒），避免 Next 启动后前几秒未监听导致误判。

---

### 实际部署说明：Docker 与 native

| 方式 | 适用场景 |
|------|----------|
| **Docker** | 本机已安装 Docker，且当前用户能访问 daemon（`docker info` 无权限错误）。`deploy.sh` 在 `BOOKGEN_DEPLOY_MODE=auto` 下会优先选此项：`compose build` + `up -d`。 |
| **native** | 无 Docker，或 **有 `docker` 命令但无 socket 权限**（常见于未加入 `docker` 组）。`auto` 会 **自动回退到 native**，并在终端说明原因。 |

**Docker「不可用」时会发生什么**

- **`BOOKGEN_DEPLOY_MODE=auto`（默认）**：检测到 CLI 存在但 `docker info` 失败时，**自动改用 native**，不中断退出。
- **强行 `BOOKGEN_DEPLOY_MODE=docker`**：若仍无法连接 daemon，**脚本以非零退出**，并提示改用 `native`。

**native 模式怎么启动**

1. **`./scripts/deploy.sh`**（`mode` 为 native 时）会：`uv sync --frozen` → `build.sh` → 默认再执行 **`./scripts/native-start.sh`**，在后台启动：
   - API：`uv run uvicorn ... --port 8001`，日志 **`.run/api.log`**
   - 前端：`npm run start`（`:8765`），日志 **`.run/web.log`**
   - PID 写在 **`.run/api.pid`**、**`.run/web.pid`**（目录已加入 `.gitignore`）
2. 若你用 **systemd / supervisor** 管进程：设置 **`BOOKGEN_NATIVE_AUTOSTART=0`**，并自行用 **`BOOKGEN_NATIVE_RESTART_CMD`** 重启服务。
3. 仅停止脚本拉起的进程：**`./scripts/native-stop.sh`**。

**OpenClaw / 服务器上推荐命令（与上表一致）**

```bash
cd /path/to/bookgen
git pull
cd backend && uv sync && cd ..
./scripts/deploy.sh
./scripts/check.sh
```

检查 URL 与部署环境一致时（HTTPS、域名、反代）：

```bash
API_URL=https://api.example.com \
FRONTEND_URL=https://www.example.com \
./scripts/check.sh
```

**`check.sh` 失败时先看哪里**

1. **端口**：`ss -tlnp | grep -E '8001|8765'`（或 `lsof -i :8001`）是否在本机监听。
2. **日志**：native 看 **`.run/api.log`**、**`.run/web.log`**；Docker 用 **`docker compose logs -f api web`**。
3. **进程**：是否被其它终端占用同一端口（先 `native-stop.sh` 或停掉旧 `uvicorn`/`next`）。
4. **拉长等待**：前端极慢时可调 **`CHECK_MAX_ATTEMPTS`** / **`CHECK_INTERVAL_SEC`**（见下）。

`check.sh` 环境变量（可选）：

| 变量 | 默认 | 含义 |
|------|------|------|
| `CHECK_MAX_ATTEMPTS` | `30` | API、首页各自最多尝试次数 |
| `CHECK_INTERVAL_SEC` | `2` | 两次尝试间隔（秒） |

### 部署脚本行为摘要

| 脚本 | 作用 |
|------|------|
| `./scripts/deploy.sh` | `uv sync --frozen`；**auto** 选 Docker 或 native；docker 则 compose；native 则 `build.sh` 后默认 **`native-start`** |
| `./scripts/check.sh` | **重试**后校验 `/api/health` 与首页 HTTP 200 |
| `./scripts/native-start.sh` | 仅 native：后台启动 API + Next（需已 build） |
| `./scripts/native-stop.sh` | 仅 native：按 `.run/*.pid` 停止上述进程 |
| `./scripts/dev.sh` | 本地开发：并行 `:8001` + `:8765`（非后台） |

环境变量：

- **`BOOKGEN_DEPLOY_MODE`**：`auto` | `docker` | `native`
- **`BOOKGEN_NATIVE_AUTOSTART`**：native 下是否自动执行 `native-start`（默认 `1`）；设为 `0` 则只构建
- **`BOOKGEN_NATIVE_RESTART_CMD`**：native 下若设置，则**代替** `native-start`（适合 systemd）

### Docker Compose 说明

- 根目录：`docker compose up -d --build`（与 `deploy.sh` 的 docker 分支一致）。
- 映射：`8001` → API，`8765` → Next；`content/` 只读挂载到 API 容器。
- 容器内前端使用 `API_URL=http://api:8001`；改端口或反代时需同步 `docker-compose.yml` 与检查脚本 URL。

## 内容目录（`content/books`）

默认内容根目录为**仓库根**下的 `content/books`（勿把内容放进 `backend/app/`）。每本书一个子目录，目录名需与 `book.json` 里的 `id` 一致：

```text
content/books/<book-id>/
  book.json
  chapters/
    001.md
    002.md
  meta/
    001.json
    002.json
  audio/
    001.mp3
    002.mp3
  assets/
    cover.jpg
```

### 新增一本书

1. 在 `content/books/` 下新建目录，例如 `my-story`。
2. 编写 `book.json`（字段见 `novel-site-spec.md`：`id`、`title`、`author`、`description`、`status`、`tags`、`cover`、`created_at`、`updated_at` 等）。**`id` 必须与目录名相同。**
3. 添加 `chapters/`、`meta/` 与可选的 `assets/`。
4. 封面路径 `cover` 若指向本站文件，可写为 `/content/books/<book-id>/assets/cover.jpg`（由 API 静态服务 `/content/...` 提供）。

### 新增一章

1. 在 `meta/` 增加 `00N.json`（`number`、`slug`、`title` 等与 `001.json` 同结构）。
2. 在 `chapters/` 增加对应 `00N.md`（Markdown 正文）。
3. 按章节号递增；目录顺序由 `meta` 中 `number` 排序决定。
4. 如果该章节有预生成音频，可在 `meta/00N.json` 增加可选字段 `"audio": "/content/books/<book-id>/audio/00N.mp3"`。

保存文件后无需数据库迁移；刷新页面即可看到更新（前端有短时 revalidate，必要时强刷）。

## 章节 TTS（edge-tts + ffmpeg，预生成）

TTS 采用离线预生成：脚本先用 `edge-tts` 生成原始语音，再用 `ffmpeg` 转码为网页兼容性更高的 MP3（`44.1kHz / 128kbps / 双声道`），最后写回章节 `meta/*.json` 的 `audio` 字段。前端章节页检测到该字段后会显示原生播放器。

运行前提：

- 已安装后端 Python 依赖（含 `edge-tts`）
- 系统已安装 `ffmpeg`（脚本启动会检查，缺失时直接报错并提示安装）

先安装后端依赖：

```bash
cd backend
uv sync
```

推荐从 `backend/` 目录执行脚本：

```bash
# 单章生成（示例：第 1 章）
cd backend
uv run ../scripts/generate_tts.py \
  --book-id city-test-begins \
  --chapter 1 \
  --overwrite

# 整本生成
uv run ../scripts/generate_tts.py \
  --book-id city-test-begins \
  --all
```

可选参数：

- `--voice`：指定 edge-tts 音色（默认 `zh-CN-XiaoxiaoNeural`）
- `--overwrite`：覆盖已有 mp3（默认跳过已存在文件）

## API（只读）

| 方法 | 路径 |
|------|------|
| GET | `/api/health` |
| GET | `/api/books` |
| GET | `/api/books/{book_id}` |
| GET | `/api/books/{book_id}/chapters/{chapter_slug}` |

不存在返回 **404**；单本书元数据损坏返回 **500** 及明确文案；章节正文缺失等返回 **503** 及说明。

## 环境变量说明

见根目录 [`.env.example`](.env.example)。后端可在 `backend/.env` 中设置 `CONTENT_ROOT`（书籍根目录，一般为 `…/content/books`）、`CORS_ORIGINS` 等。

## 验收对照

1. 前后端可本地启动（`scripts/dev.sh`）。
2. 首页有书目列表；可进详情与章节阅读。
3. 新增章节文件后站点可展示。
4. 本文档与 `novel-site-spec.md` 一致可复现。
