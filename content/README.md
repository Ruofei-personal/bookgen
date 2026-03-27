# 内容目录说明（文件发布规范）

本目录为**小说唯一内容源**：后端只读这里的文件，**不依赖数据库**。自动化工具（如 OpenClaw）应通过 **新增/修改文件 + 部署** 发布，并遵守下列规则，以保证站点稳定解析。

**内容根路径**：默认指向仓库根下的 `content/books/`（每本书一个子目录）。勿把书目录放进 `backend/`。

---

## 1. 目录结构（每本书）

```text
content/books/<book-id>/
  book.json              # 书目元数据（必填）
  chapters/
    001.md               # 第 1 章正文（Markdown）
    002.md
    ...
  meta/
    001.json             # 第 1 章元数据（建议文件名与章节号对齐）
    002.json
    ...
  assets/                # 可选：封面等静态资源
    cover.jpg
```

- **`<book-id>`**：目录名 = `book.json` 里的 **`id`**，且与 API/URL 中的 `book_id` 一致（例如 `/books/example-book`）。
- **`chapters/` 与 `meta/`**：缺一则该侧视为无章节；`meta` 里单文件 JSON 损坏会被**跳过**（该章不出现），不会拖垮整站。

---

## 2. `book.json` 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 与上级目录名 **`books/<id>`** 必须相同；站点与 API 用其定位本书。 |
| `title` | string | 是 | 书名。 |
| `author` | string | 否 | 默认可 `""`。 |
| `description` | string | 否 | 简介；默认可 `""`。 |
| `status` | string | 否 | **`"ongoing"`**（连载）或 **`"completed"`**（完结）；省略时后端按 **`ongoing`** 处理，发布脚本建议始终写出。 |
| `tags` | string[] | 否 | 标签列表；可 `[]`。 |
| `cover` | string \| null | 否 | 封面地址：`null` 无封面；相对路径建议以 **`/content/books/<id>/assets/...`** 开头（由 API 静态服务）；也可填完整 `http(s)://...`。 |
| `created_at` | string \| null | 否 | ISO 8601 时间，如 **`2026-03-28T00:00:00Z`**。 |
| `updated_at` | string \| null | 否 | ISO 8601；**首页书目排序**按此字段（新在前）。见下文「更新时间规则」。 |
| `latest_chapter_title` | string \| null | 否 | 最新章节标题展示用；可省略，由后端用**当前最大章节号**一章的 `title` 自动补全。 |
| `latest_chapter_number` | int \| null | 否 | 最新章节号；可省略，由后端按章节列表自动补全。 |

**约束**：须为合法 **JSON**，UTF-8 编码。单本书 `book.json` 若无法解析，该书在列表中可能被跳过或详情报错，发布前务必校验。

---

## 3. 章节元数据 `meta/*.json`

每个章节一个 JSON 文件，扩展名 **`.json`**；文件名建议 **`NNN.json`**（与章节编号一致），便于人工与脚本对齐——**排序以字段 `number` 为准，不以文件名为准**。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 章节在本书范围内的唯一 ID（可与 `slug` 相同或不同，保持唯一即可）。 |
| `book_id` | string | 是 | 必须与本书 **`book.json` 的 `id`** 一致。 |
| `number` | int | 是 | 章节序号，**正整数**；与正文文件名 **`chapters/NNN.md` 中的 NNN** 一致（见下节）。 |
| `title` | string | 是 | 章节标题（展示用）。 |
| `slug` | string | 是 | **URL 片段**，用于阅读页路径：`/books/<book-id>/chapters/<slug>` 及 API `.../chapters/<slug>`。 |
| `created_at` | string \| null | 否 | ISO 8601。 |
| `updated_at` | string \| null | 否 | ISO 8601；建议章节有改动时更新。 |
| `summary` | string \| null | 否 | 摘要，可选。 |

**同一本书内 `slug` 必须唯一**；若重复，解析时以**先匹配到的一条**为准（应避免重复）。

---

## 4. 章节编号与正文文件 `chapters/NNN.md`

- **`number`** 与 Markdown 文件名严格对应：**三位零填充**。
  - `number: 1` → 文件 **`chapters/001.md`**
  - `number: 12` → **`chapters/012.md`**
- 正文为 **Markdown**（UTF-8）；缺失对应 `NNN.md` 时，访问该章会报错（503），发布前须保证 **每个在 `meta` 中出现的 `number` 都有同名 `chapters/NNN.md`**。

---

## 5. `slug` 规则（稳定 URL）

自动化发布请固定下列约定，避免链接失效：

1. **在单本书内全局唯一**，且与 `number` / 文件名一一对应（例如第 3 章固定 `chapter-003` 或自定义前缀 + 三位数）。
2. 建议 **仅使用**：小写字母、数字、连字符 **`[a-z0-9-]`**，避免空格与中文直出 URL（减少编码与复制问题）。
3. 与 **`meta` 文件名无强制绑定**；阅读与 API 只认 JSON 内的 **`slug`** 与 **`number`**。

**示例**（与 `number: 1` 配套）：

```json
"slug": "chapter-001"
```

---

## 6. `updated_at` 更新规则（建议）

便于首页「按更新时间排序」与运维感知：

| 对象 | 建议 |
|------|------|
| **`book.json` 的 `updated_at`** | 每次本书有**任意对外可见变更**时更新（新书目、新章、改章、改简介/封面/状态等）。首页列表按此排序。 |
| **章节 `meta` 的 `updated_at`** | 该章正文或元数据（标题、摘要等）变更时更新。 |
| **`created_at`** | 首次发布时可写；后续不必每次改章都改 `created_at`。 |

时间格式统一为 **ISO 8601**，推荐带 **`Z`** 的 UTC，例如：`2026-03-28T12:00:00Z`。

---

## 7. OpenClaw / 自动化发布检查清单

1. `content/books/<id>/` 存在且 **`id` 与目录名一致**。  
2. `book.json` 合法 JSON，**`status` 仅 `ongoing` 或 `completed`**。  
3. 新章：在 `meta/` 增加 `NNN.json`，在 `chapters/` 增加 **`NNN.md`**，`number` 与文件名一致，`slug` 唯一。  
4. 更新 **`book.json` 的 `updated_at`**（及可选 `latest_*` 或依赖后端自动补全）。  
5. 部署后可用仓库根目录 **`./scripts/check.sh`** 做健康检查（见主 `README.md`）。

更宏观的产品说明见仓库根目录 **`novel-site-spec.md`**。
