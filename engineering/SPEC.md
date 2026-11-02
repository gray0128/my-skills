---
id: engineering
type: module-design
parent: architecture
status: draft
title: engineering 主题：软件工作的判断、治理与交付
---

## Responsibility

覆盖软件工作从"看清现状"到"改动落地"的完整链条：判断代码与评审意见是否站得住、建立让判断可复用的规则、按规则把工作项推进成可交付的改动。

本主题的技能都作用于同一批对象——代码、PR、Issue、契约——区别只在**允许改动到什么程度**。

## 权限梯度

这是本主题的组织原则，也是选择技能时的第一判断：拿到一个请求，先问"它要求我改到什么程度"。

| 档位 | 被允许的写入 | 技能 |
|---|---|---|
| 判断 | 只产出结论；不改被评审对象的实现 | `brutal-advisor`、`code-review`、`pr-review`、`analyze-review-conclusion`、`audit-contract-governance` |
| 建规则 | 只写治理制品（指令、契约、跟踪器、门禁配置） | `bootstrap-contract-governance` |
| 改代码 | 改产品代码，范围受已接受的计划约束 | `contract-first-delivery-loop`、`issue-handler` |

判断档内部的产物形态各不相同，选技能时看后一张表：`code-review` 与 `audit-contract-governance` 只回结论（后者硬性禁止创建或修改任何仓库文件），`analyze-review-conclusion` 写一份报告文件，`pr-review` **默认**向平台提交 review，只在用户明确要求或权限不足时才降为聊天回复。共同点只有一个：都不动被评审的实现。

档位互斥：一次调用只落在其中一档。审计发现问题后要修，属**另一次**调用 `bootstrap-contract-governance`，不复用审计的授权。因此这几个技能不构成必须按序执行的流水线，而是按需组合。

## Skills

| 技能 | 档位 | 产物 | 何时用 |
|---|---|---|---|
| `brutal-advisor` | 判断 | 聊天回复 | 对方案、方向或决策做战略层面的加压审视：追根因、暴露盲区与机会成本、重定义问题 |
| `code-review` | 判断 | 聊天回复 | 对代码或 diff 做严苛的可维护性审查（抽象质量、巨型文件、分支爆炸） |
| `pr-review` | 判断 | 平台 review（默认），必要时聊天 | 对 GitHub PR 做证据绑定评审，绑定当前 head SHA |
| `analyze-review-conclusion` | 判断 | `评审报告分析采纳结论.md` | 手上已有一份评审结论或审计报告，要判断该不该采纳 |
| `audit-contract-governance` | 判断 | 聊天回复，不写文件 | 判断仓库的契约、跟踪器、验证门禁是否自洽 |
| `bootstrap-contract-governance` | 建规则 | 治理制品 | 安装、迁移或修复最小可用治理面 |
| `contract-first-delivery-loop` | 改代码 | 代码 + 契约 + 跟踪器 | 在既有治理体系下交付一个已跟踪、可独立验证的实现切片 |
| `issue-handler` | 改代码 | 代码 + PR | 从一条 Issue 出发，取上下文、发计划、实现、开 PR |

## Invariants

**计划先于代码.** 动产品代码前，先把实施计划落地成可被他人审查的形态（Issue 评论或等价物）。例外只有两种：为理解仓库所做的只读探查，以及用户明确要求只出本地草稿、不碰跟踪器。跟踪器不可达不构成例外——那是阻塞项，应停下上报。

**判断不收尾.** 判断档的技能不改被评审对象的实现、不合并 PR、不解决对话；收尾动作仅在用户明确授权或编排策略要求时发生。

**显式调用优先.** 治理三件与 `code-review` 都以用户点名为主：治理动作会改仓库的权威结构，`code-review` 的判定尺度比日常审查严苛，两者误触发的代价都高于漏触发。

**署名真实.** 提交物中标注的 Agent 与模型名必须与实际执行者一致，不允许套用他人的署名模板。
