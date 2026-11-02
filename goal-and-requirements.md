---
id: goal
type: goal-and-requirements
status: draft
title: 个人 Agent Skills 集合
tags: [skills, agent]
---

## Goal

本仓库是作者个人维护的 Agent Skills 单一来源：每个技能是一份供 Claude Code、Codex、Pi、Grok 等宿主读取的操作说明，作者按需把它们安装到各宿主的 skills 目录，而不是在每个宿主里各自维护一份。

仓库存在的理由是可复用与可携带：同一份技能内容能被多个宿主共享，也能分发给他人安装，同时避免同一主题的技能在仓库里散落成一堆平级目录。

## Audience

仓库作者本人，其次是希望复用其中部分技能的他人。

## Capabilities

- 收纳彼此独立的 agent 技能，每个技能自带 `SKILL.md`（含 `name` 与 `description` frontmatter）以及可选的 `references/`、`assets/`、`scripts/`、`tests/`、`evals/`、`agents/`。技能正文是供宿主阅读的说明文档；`scripts/` 可以携带由宿主在运行技能时调用的辅助脚本（如批量调 CLI 的分发器、报告校验脚本），有测试时放在该技能的 `tests/` 下。
- 技能按主题归类，主题随技能增长而增减：新技能找不到合适归属时新建主题，而不是塞进一个不对的归类。
- 每个技能可单独装到任一宿主，不必整包搬运。
- 提供双语 README，说明目录结构、每个技能的职责与安装方式。

## Non-goals

- 不做宿主级的技能加载器：仓库不提供加载、发现、调度技能正文的运行时。技能内嵌的辅助脚本只服务自己那一个技能，不构成仓库级运行时。
- 不做包管理与版本发布机制：技能不做成可执行程序或 npm 包发布，分发靠复制目录或 `skills` CLI 从仓库拉取。
- 不追求覆盖所有平台：仓库只保留作者实际在用的技能，平台专用技能随使用场景增减。
- 不托管与本仓库职责无关的项目代码或产品仓库。

## Principles

- **技能之间彼此独立**：单个技能目录自包含，不依赖仓库内其他技能的存在。
- **说明写给人也写给 Agent**：`description` 要写清“何时该用这个技能”，它是技能可用性的前提。

命名、安装与触发机制的完整约束统一由 [`architecture`](architecture.md) 定义，此处不重述。
