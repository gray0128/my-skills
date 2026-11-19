---
name: single-file-docs-site
description: 将仓库内多篇 Markdown 文档与本地图片打包为零外部依赖、可离线打开的三栏单页 HTML 文档站，并提供脚手架初始化与一致校验。在用户要求把 Markdown 文档整理成单文件离线站点、初始化或同步更新 docs/site/ 模板与清单、内嵌本地截图或校验 docs/index.html 与源文件一致时使用。
---

# 单文件离线文档站（single-file-docs-site）

内置模板 [assets/template.html](assets/template.html) 与零依赖构建脚本 [scripts/build-docs.mjs](scripts/build-docs.mjs) 将一组 Markdown 与本地图片打包为单个自包含 HTML（左栏分组导航、中栏正文、右栏吸顶目录、原生 `<dialog>` `⌘K` 全文搜索与移动端抽屉）。

## 使用方式

按目标仓库是否需要把生成脚本纳入长期维护选一种方式：

- **长期纳入目标仓库**：复制 [scripts/build-docs.mjs](scripts/build-docs.mjs) 到目标仓库 `scripts/build-docs.mjs`，并在目标仓库 `package.json` 添加 `"build:docs": "node scripts/build-docs.mjs"` 与 `"check:docs": "node scripts/build-docs.mjs --check"`。
- **临时或只读生成**：在当前技能目录内直接执行 `node scripts/build-docs.mjs ... --docs-dir <目标文档目录>`。

## 标准流程

### 1. 初始化站点真源（首次接入）

目标目录下尚无 `site/manifest.json` 时，在技能目录内执行：

```bash
node scripts/build-docs.mjs --init --docs-dir <目标文档目录>
```

脚手架会扫描全部 `.md` 文件生成 `site/manifest.json` 并复制模板到 `site/template.html`。若目录已存在 `site/` 且需重建，追加 `--force`。

### 2. 调整 `site/manifest.json`

按阅读顺序与展示习惯整理生成的 `site/manifest.json`：

- 根级 `.md` 文件的分组 `dir` 为 `""`，子目录用相对目录名（如 `"design"`）。
- `docs[]` 的顺序决定侧栏、搜索列表及上下篇翻页顺序。
- 随包非站点 Markdown（如独立手册、临时草稿）写入 `"ignore": [...]`，避免触发未登记报错。

| 字段 | 必需 | 说明 |
|---|---|---|
| `version` / `updatedAt` | 否 | 写入页脚版本前缀 |
| `site.lang` / `title` / `brand` / `subtitle` / `sourceHint` | 否 | 覆盖页面 `<html lang>`、`<title>`、顶栏标题、副标题与页脚源目录提示 |
| `groups[]` | 是 | `{ dir, label }` 列表；`dir` 唯一，`dir: ""` 对应根目录文档 |
| `docs[]` | 是 | `{ id, label, file, title? }` 列表；缺省 `title` 时提取首个非代码块 `# 标题` |
| `ignore[]` | 否 | 排除扫描的相对 `.md` 路径列表 |

### 3. 构建并校验产物

```bash
node scripts/build-docs.mjs --docs-dir <目标文档目录>
node scripts/build-docs.mjs --check --docs-dir <目标文档目录>
```

目标仓库已拷贝 `scripts/build-docs.mjs` 时，改为在目标仓库根目录运行 `npm run build:docs` 与 `npm run check:docs`。

构建与校验门禁覆盖以下故障并在发现时中止退出：

- 磁盘存在未登记进 `manifest.json` 且不在 `ignore` 中的 `.md` 文件（输出可直接粘贴的条目提示）。
- `manifest.json` 引用的文档缺失、缺少一级标题且未显式指定 `title`，或 `id`/`file` 重复。
- Markdown 引用的相对图片不存在、路径越界或格式不受支持（支持 `.png`、`.jpg`/`.jpeg`、`.gif`、`.webp`、`.svg`；代码块与行内代码中的图片语法会自动跳过）。
- JSON 载荷存在未转义闭合标签（构建自动将 `</`、`<!--`、`\u2028`、`\u2029` 转义并用函数替换注入，保证 `</script>` 与 `$&`/`$'`/`$$`/`$1` 原样还原）。
- 目标 `index.html` 与源文件不一致（`--check` 退出非零）；一致时重跑构建为幂等空操作。

### 4. 自定义模板占位符

定制目标仓库 `site/template.html` 时需保留以下占位符：

- **必选（恰好出现 1 次）**：`<!--__FOOTER_META__-->`、`<!--__DOC_DATA__-->`、`<!--__ASSET_DATA__-->`。
- **可选（最多出现 1 次）**：`__SITE_LANG__`、`<!--__SITE_TITLE__-->`、`<!--__SITE_BRAND__-->`、`<!--__SITE_SUBTITLE__-->`、`<!--__SOURCE_HINT__-->`。

## 自测

修改本技能的脚本或模板后，在技能目录内执行内置测试套件：

```bash
node tests/build-docs.test.mjs
```
