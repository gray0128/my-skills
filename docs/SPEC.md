---
id: docs
type: module-design
parent: architecture
status: draft
title: docs 主题：文档构建与交付
---

## Responsibility

将仓库内的多篇 Markdown 文档与配套本地资源整理、打包并校验为可离线阅读或分发的文档成品。与 `design` 的区别在于面向结构化技术文档交付而非一次性视觉原型；与 `engineering` 的区别在于直接生成并校验文档产物而非仅输出评审判断。

## Skills

| 技能 | 何时用 |
|---|---|
| `single-file-docs-site` | 将多篇 Markdown 与本地图片打包为可离线打开的三栏单页 HTML 文档站，并提供脚手架初始化与一致性校验 |

## Invariants

**真源与生成物分离.** `manifest.json`、`template.html` 与源 Markdown/图片是唯一真源；生成产物（如 `index.html`）严禁直接手改，必须通过脚本重建。

**零外部运行时依赖.** 离线文档产物不得引用外链 CDN 脚本或样式，图片等静态资源按需内嵌并确保在 `file://` 下完整可用。

**确定性与自检门禁.** 相同输入连续构建产出逐字节一致；漏登记文档、缺失图片、未转义闭合标签或主脚本语法错误必须在构建期 Fail-fast 报错。
