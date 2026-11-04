---
id: engineering
type: module-design
parent: architecture
status: draft
title: engineering 主题：对软件工作的判断
---

## Responsibility

对方案、方向或决策做判断：追根因、暴露盲区，给出可执行的结论。不改被审视对象的实现。

## 权限梯度

本主题当前只有判断一档：只产出结论，不改被审视对象的实现，不合并 PR，不解决对话。

## Skills

| 技能 | 档位 | 产物 | 何时用 |
|---|---|---|---|
| `brutal-advisor` | 判断 | 聊天回复 | 对方案、方向或决策做战略层面的加压审视：追根因、暴露盲区与机会成本、重定义问题 |

## Invariants

**判断不收尾.** 判断档的技能不改被审视对象的实现、不合并 PR、不解决对话；收尾动作仅在用户明确授权或编排策略要求时发生。
