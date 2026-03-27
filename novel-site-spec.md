# 小说发布网站规格说明（给 Cursor / Codex）

## 目标

做一个**极简的小说发布网站**，面向公开访问，不做登录、不做后台管理系统、不做支付、不做评论。

核心目标：
- 可以展示小说列表
- 可以进入小说详情页
- 可以按章节阅读
- 支持后续由 OpenClaw 通过文件/命令方式自动发布新章节
- 架构尽量简单、稳定、低维护成本

该网站未来的使用模式：
- 人类通过 Discord / WhatsApp 指挥 OpenClaw
- OpenClaw 负责把小说内容整理、落盘、部署上线
- Cursor / Codex 负责实现网站本身

所以整个系统要**优先考虑可维护性、可脚本化、可自动发布**，而不是复杂功能。

---

## 技术栈要求

### 后端
- 使用 **Python**
- 使用 **uv** 管理 Python 项目和依赖
- 推荐框架：**FastAPI**
- 提供 JSON API
- 代码结构清晰，便于后续 OpenClaw 调用脚本或直接改内容文件

### 前端
- 使用 **Node.js**
- 推荐框架：**Next.js** 或 **Astro**
- 优先选择实现简单、页面清晰、SEO 友好的方案
- 前端负责展示，不做复杂客户端状态管理

### 存储
优先级如下：
1. **文件存储优先**（推荐）
2. SQLite 可作为补充，但不是必须

推荐内容存储方式：
- 每本书一个目录
- 书籍元数据一个文件
- 每章一个 Markdown 或 JSON 文件

原因：
- 方便 OpenClaw 直接写文件发布
- 方便 git 管理与备份
- 不依赖复杂数据库
- 更适合小型内容站

---

## 产品范围（第一版）

### 必做页面

1. **首页**
   - 展示网站标题
   - 展示小说列表
   - 每本书显示：
     - 书名
     - 简介
     - 封面（可选）
     - 标签 / 类型
     - 最新章节标题
     - 更新时间

2. **小说详情页**
   - 显示书名、简介、封面、标签
   - 显示章节目录
   - 章节按顺序展示
   - 可显示是否连载中

3. **章节阅读页**
   - 显示章节标题
   - 显示正文
   - 有“上一章 / 下一章 / 返回目录”
   - 页面干净，适合长文本阅读
   - 支持基础排版（段落、标题、引用即可）

### 可选页面
4. **关于页**
   - 简单介绍网站用途

### 第一版明确不做
- 用户登录
- 用户注册
- 评论系统
- 点赞
- 书架
- 支付
- 权限系统
- CMS 后台
- 搜索（如果后面要加，可以第二版再做）

---

## 信息架构

### 数据模型

#### Book（书籍）
建议字段：
- `id`: 唯一 ID（slug）
- `title`: 书名
- `author`: 作者名（可默认固定）
- `description`: 简介
- `status`: `ongoing` / `completed`
- `tags`: 字符串数组
- `cover`: 封面路径（可为空）
- `created_at`
- `updated_at`
- `latest_chapter_title`
- `latest_chapter_number`

#### Chapter（章节）
建议字段：
- `id`: 章节 ID
- `book_id`
- `number`: 第几章
- `title`: 章节标题
- `slug`: URL slug
- `created_at`
- `updated_at`
- `summary`: 可选
- `content`: 正文（Markdown）

---

## 推荐文件结构

下面是推荐结构，Cursor 可按这个实现，允许适度调整，但要保持“人类和 OpenClaw 都能直接读写”的特点。

```text
project-root/
  backend/
    pyproject.toml
    app/
      main.py
      api/
      services/
      models/
      content/
        books/
          example-book/
            book.json
            chapters/
              001.md
              002.md
            meta/
              001.json
              002.json
            assets/
              cover.jpg

  frontend/
    package.json
    src/
      pages/ or app/
      components/
      lib/
```

### 内容文件约定

每本书目录示例：

```text
books/my-first-book/
  book.json
  chapters/
    001.md
    002.md
  meta/
    001.json
    002.json
  assets/
    cover.jpg
```

#### `book.json` 示例
```json
{
  "id": "my-first-book",
  "title": "我的第一本书",
  "author": "Jeff",
  "description": "这是一本测试小说。",
  "status": "ongoing",
  "tags": ["玄幻", "连载"],
  "cover": "/content/books/my-first-book/assets/cover.jpg",
  "created_at": "2026-03-28T00:00:00Z",
  "updated_at": "2026-03-28T00:00:00Z"
}
```

#### `meta/001.json` 示例
```json
{
  "id": "chapter-001",
  "book_id": "my-first-book",
  "number": 1,
  "title": "第一章 尸坑",
  "slug": "chapter-001",
  "created_at": "2026-03-28T00:00:00Z",
  "updated_at": "2026-03-28T00:00:00Z",
  "summary": "矿洞塌陷后，主角被扔进尸坑。"
}
```

#### `chapters/001.md` 示例
```md
# 第一章 尸坑

正文内容……
```

---

## 后端要求

### API 设计
第一版至少提供以下接口：

1. `GET /api/books`
   - 返回书籍列表
   - 按更新时间倒序

2. `GET /api/books/{book_id}`
   - 返回书籍详情
   - 包含章节目录

3. `GET /api/books/{book_id}/chapters/{chapter_slug}`
   - 返回章节详情
   - 包含正文
   - 返回上一章 / 下一章信息

4. `GET /api/health`
   - 健康检查接口
   - 返回简单 JSON

### 可选但强烈建议的内部接口
这些接口可以先不暴露到公网，但要为后续 OpenClaw 自动发布预留：

5. `POST /api/internal/books`
   - 创建一本书

6. `POST /api/internal/books/{book_id}/chapters`
   - 新增章节

7. `PATCH /api/internal/books/{book_id}`
   - 更新书籍元数据

8. `DELETE /api/internal/books/{book_id}/chapters/{chapter_slug}`
   - 删除章节（如做该接口，必须是内部使用）

这些内部接口可以先通过：
- 本地调用
- 环境变量中的简单 token
- 或只绑定 127.0.0.1

不要做复杂鉴权系统。

### 内容处理要求
- 后端需要能读取 Markdown 文件并转换为 HTML 或结构化内容
- 推荐使用安全的 Markdown 渲染方案，避免原始 HTML 注入
- 要处理章节排序
- 要能快速重建目录缓存（如果做缓存）

### 错误处理
- 书不存在 → 404
- 章节不存在 → 404
- 内容文件损坏 → 返回可读错误日志，不要整个服务崩掉

---

## 前端要求

### 首页
- 干净、轻量
- 小说卡片式列表
- 适配桌面和移动端
- 不要搞很重的炫技动画

### 小说详情页
- 上方显示书名、简介、标签、状态
- 下方是章节目录
- 章节目录清晰可点击

### 阅读页
- 重点是阅读体验
- 字体、行高、段落间距舒适
- 手机端阅读要舒服
- 提供：
  - 上一章
  - 下一章
  - 返回目录
- 页面不要太花

### SEO / 基础元信息
- 每本书页面有独立 title / description
- 每章页面有独立 title
- 尽量保证搜索引擎友好

---

## 运维与部署要求

这个部分很重要，因为未来 OpenClaw 会负责运维。

### 总体原则
- 部署流程必须简单
- 最好一条命令可启动
- 最好一条命令可构建
- 配置通过 `.env` 管理
- 日志清晰

### 后端要求
- 提供开发启动命令
- 提供生产启动命令
- 支持 `uv` 管理依赖

建议：
- 开发：`uv run uvicorn app.main:app --reload`
- 生产：`uv run uvicorn app.main:app --host 0.0.0.0 --port 8000`

### 前端要求
- 提供开发命令
- 提供构建命令
- 提供生产运行命令

### Docker
**强烈建议提供 docker-compose 方案**，即使第一版不强制要求全 Docker 化，也建议预留。

推荐至少提供：
- `docker-compose.yml`
- 前端服务
- 后端服务
- 可选 Nginx/Caddy 反代

### 健康检查
- 后端：`/api/health`
- 前端：首页可访问
- 如果用 Docker，建议写 healthcheck

### 环境变量
至少支持：
- `BACKEND_HOST`
- `BACKEND_PORT`
- `FRONTEND_PORT`
- `CONTENT_ROOT`
- `INTERNAL_API_TOKEN`（如果实现内部接口）

---

## OpenClaw 集成要求（非常重要）

这个网站后续会由 OpenClaw 运维和发布内容，所以请 Cursor / Codex 实现时优先满足以下要求：

1. **内容可文件化管理**
   - OpenClaw 可以直接新增/修改书籍文件和章节文件

2. **部署过程脚本化**
   - 提供清晰命令，如：
     - `make dev`
     - `make build`
     - `make start`
     - `make deploy`
   - 或 shell 脚本：
     - `scripts/dev.sh`
     - `scripts/build.sh`
     - `scripts/deploy.sh`

3. **日志清晰**
   - 出错时便于 OpenClaw 排查

4. **不要把内容写死在数据库里**
   - 第一版尽量文件驱动

5. **尽量减少隐藏魔法**
   - 目录结构、配置文件、运行方式都要直白

6. **README 要完整**
   - 写清楚本地开发、构建、部署、内容发布方式

---

## 建议的开发顺序

### Phase 1
- 后端读取文件内容
- 提供书籍列表 API
- 提供书详情 API
- 提供章节详情 API
- 前端完成 3 个页面：首页 / 书详情 / 阅读页

### Phase 2
- 完善样式
- 增加封面支持
- 增加关于页
- 增加内部发布接口

### Phase 3
- Docker 化
- 增加部署脚本
- 增加缓存/构建优化

---

## 验收标准

项目完成后，至少应满足：

1. 可以本地启动前后端
2. 首页可看到书籍列表
3. 可进入某本书详情页
4. 可点击章节阅读正文
5. 新增一个章节文件后，网站能正确显示
6. 服务重启后内容不丢失
7. README 写清楚如何：
   - 启动
   - 构建
   - 部署
   - 新增一本书
   - 新增一章

---

## 额外建议

- 代码风格优先朴素、稳定，不要过度工程化
- 第一版不要引入复杂数据库迁移体系
- 第一版不要做账号系统
- 第一版不要做富文本后台
- 这个项目的本质是“可被 OpenClaw 维护的轻量小说站”

---

## 一句话总结

请实现一个：

**基于 Python(FastAPI) + uv + Node.js 前端的极简小说发布网站，使用文件作为主要内容源，支持公开阅读，便于 OpenClaw 后续通过脚本/文件自动发布和运维。**
