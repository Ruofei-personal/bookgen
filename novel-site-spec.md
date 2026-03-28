# bookgen 网站规格说明

## 项目定位

这是一个**极简小说发布网站**。

目标很简单：
- 公开展示小说
- 浏览书籍列表
- 查看书籍详情
- 阅读章节正文
- 后续方便通过文件或脚本自动发布新章节

**明确不做：**
- 登录 / 注册
- 用户系统
- 评论
- 支付
- 后台 CMS
- 复杂权限控制

这是一个内容站，不是社区，不是 SaaS。

---

## 技术栈

### 后端
- Python
- 使用 `uv` 作为**唯一的 Python 项目与依赖管理方式**
- FastAPI

后端必须满足：
- 使用标准 `uv` 项目结构
- 包含 `pyproject.toml`
- 包含 `uv.lock`
- 依赖通过 `uv add` / `uv sync` 管理
- 运行命令统一使用 `uv run ...`
- 不要把 `requirements.txt` 作为主依赖管理方式

### 前端
- Node.js
- Next.js

### 存储
- **文件优先**，不要以数据库作为核心内容源
- 第一版可以完全不接数据库
- 如果后面确实有需要，SQLite 只能做辅助，不能绑死内容

---

## 核心设计原则

1. **简单优先**
2. **文件驱动优先**
3. **方便部署和运维**
4. **方便后续 OpenClaw 自动更新内容**
5. **适合单人维护的小网站**

---

## 页面需求

### 1. 首页
展示：
- 网站标题
- 小说列表
- 每本书展示：
  - 书名
  - 简介
  - 标签
  - 封面（可选）
  - 最新章节
  - 更新时间

### 2. 小说详情页
展示：
- 书名
- 简介
- 标签
- 状态（连载中 / 已完结）
- 章节目录

### 3. 章节阅读页
展示：
- 章节标题
- 正文内容
- 上一章 / 下一章 / 返回目录

要求：
- 移动端可读性好
- 页面简洁
- 不做复杂动效

---

## 内容结构

推荐目录结构如下：

```text
content/
  books/
    my-first-book/
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

### 额外要求
- `content/` 目录放在**项目根目录**，不要塞进 `backend/app/` 里面
- 内容文件应当能被人类直接编辑，也方便 OpenClaw 后续直接写入

### 书籍元数据 `book.json`
字段建议：
- `id`
- `title`
- `author`
- `description`
- `status`
- `tags`
- `cover`
- `created_at`
- `updated_at`

### 章节元数据 `meta/001.json`
字段建议：
- `id`
- `book_id`
- `number`
- `title`
- `slug`
- `created_at`
- `updated_at`
- `summary`（可选）
- `audio`（可选，示例：`/content/books/<book-id>/audio/001.mp3`，仅预生成文件）

### 章节正文
- 使用 Markdown
- 一章一个文件

---

## API 要求

后端第一版至少提供：

- `GET /api/health`
- `GET /api/books`
- `GET /api/books/{book_id}`
- `GET /api/books/{book_id}/chapters/{chapter_slug}`

要求：
- 不存在的书 / 章节返回 404
- 内容文件损坏时要有清晰错误，不要整个服务崩掉
- 能正确按章节顺序返回目录

### 重要约束
- **第一版先只做读取内容的接口**
- **不要实现后台系统**
- **不要优先实现写接口**
- 后续如果需要 OpenClaw 自动发布，可以再补内部写接口

### 第二阶段可预留（不是第一版必须）
- `POST /api/internal/books`
- `POST /api/internal/books/{book_id}/chapters`
- `PATCH /api/internal/books/{book_id}`

如果未来实现这些接口：
- 不需要复杂鉴权
- 可通过本地调用或简单 token 控制
- 不要演化成大而全后台

---

## 前端要求

### 首页
- 清爽、轻量
- 小说列表可读性强
- 兼容手机和桌面

### 小说页
- 目录清晰
- 书籍信息集中展示

### 阅读页
- 字号、行高、段距舒服
- 适合长文本阅读
- 手机端阅读体验优先

---

## 部署要求

项目需要便于后续运维。

### 后端
建议命令：
- 初始化依赖：`uv sync`
- 开发：`uv run uvicorn app.main:app --reload`
- 生产：`uv run uvicorn app.main:app --host 0.0.0.0 --port 8001`

### 前端
需要有：
- 开发命令
- 构建命令
- 生产启动命令

### 建议提供
- `docker-compose.yml`
- `.env.example`
- `scripts/dev.sh`
- `scripts/build.sh`
- `scripts/deploy.sh`

---

## README 必须写清楚

需要清楚写出：
- 如何使用 `uv` 初始化和同步后端依赖
- 如何本地启动
- 如何构建
- 如何部署
- 如何新增一本书
- 如何新增一章
- 内容目录结构说明

---

## OpenClaw 集成要求

这个项目未来会由 OpenClaw 做发布和运维，所以实现时必须满足：

1. 内容可以直接通过文件新增 / 修改
2. 不要把内容锁死在数据库
3. 目录结构清晰
4. 部署命令直白
5. 日志可读
6. 不要引入没必要的复杂工程化

---

## 验收标准

至少满足：
1. 前后端可本地启动
2. 首页可看到书籍列表
3. 可进入小说详情页
4. 可进入章节阅读页
5. 新增章节文件后网站可显示
6. README 完整

---

## 一句话总结

请实现一个：

**基于 Python + FastAPI + uv + Next.js 的极简小说发布网站，以文件作为主要内容源，适合公开阅读，并便于后续用 OpenClaw 自动发布和运维。**
