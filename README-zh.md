# my-skills

[English](./README.md) | [简体中文](./README-zh.md)

个人 Agent Skills 集合，按主题目录分组。

## 目录结构

| 目录 | 覆盖范围 |
|------|----------|
| [engineering/](./engineering/) | 判断软件工作、建立其运行规则，并按规则交付 |
| [tools/](./tools/) | 驱动外部程序与平台 |
| [design/](./design/) | 设计不像机器生成的界面 |
| [data/](./data/) | 按 HTTP 接口拉取业务数据 |

分组只影响仓库组织方式：每个 skill 保留自己的目录名，因此安装 `engineering/code-review` 得到的技能名仍是 `code-review`。主题是开放集合——新技能找不到合适归属时，新建一个主题，而不是塞进一个不对的主题。

## Skills

### engineering/

本主题的技能作用于同一批对象（代码、PR、Issue、契约），区别在于**允许改动到什么程度**。先按这个判断选技能。

| Skill | 产物 | 说明 |
|-------|------|------|
| [brutal-advisor](./engineering/brutal-advisor/) | 聊天回复 | 直言不讳的战略顾问与认知镜子：追根因与假设审计、盲区与机会成本、重定义问题、按优先级排序的行动方案 |
| [code-review](./engineering/code-review/) | 聊天回复 | 严苛可维护性审查：抽象质量、巨型文件、意大利面条式分支增长；Grok Build `/code-review`（源自 Cursor thermo-nuclear） |
| [pr-review](./engineering/pr-review/) | 默认提交平台 review | 基于证据的 GitHub PR 评审工作流，绑定当前 HEAD SHA |
| [analyze-review-conclusion](./engineering/analyze-review-conclusion/) | `评审报告分析采纳结论.md` | 把评审结论逐条对照项目真实状态核实，产出采纳/不采纳/需人工决策结论 |
| [audit-contract-governance](./engineering/audit-contract-governance/) | 聊天回复，不写文件 | 对仓库的契约治理体系执行只读、基于证据的审计 |
| [bootstrap-contract-governance](./engineering/bootstrap-contract-governance/) | 仅治理制品 | 在现有仓库中安装或迁移最小化契约治理体系 |
| [contract-first-delivery-loop](./engineering/contract-first-delivery-loop/) | 范围内的代码、契约、测试与跟踪器 | 在既有契约约束下执行一个已跟踪、可独立验证的实现切片 |
| [issue-handler](./engineering/issue-handler/) | 代码与 PR | 通用的 Issue 到 PR 工作流，包含方案评论及 Agent/模型署名，适用于 GitHub、CNB、GitLab、Jira 等跟踪器 |

后三个构成一套契约治理技能，按**修改权限边界**而非流程阶段切分：**审计**（只读）→ **治理引导**（只写治理制品）→ **交付**（在契约下改产品代码）。它不是必须按序执行的流水线，前置条件满足时每个都能单独调用。审计与修复是两次独立调用，修复不继承审计的授权。

### tools/

本主题的技能操作别人提供的执行环境。宿主装了哪些程序、浏览器登录了哪个账号，属于**环境依赖**而非仓库依赖——缺依赖时技能按失败分类上报，不假装成功。

| Skill | 说明 |
|-------|------|
| [multi-agent-cli-dispatch](./tools/multi-agent-cli-dispatch/) | 将同一任务并行分发给多个编程 Agent CLI（`claude`、`grok`、`reasonix`、`codebuddy`、`agy`），并做超时、日志与结果分类 |
| [x-com-post](./tools/x-com-post/) | 通过 `agent-browser` 和 Chrome 用户配置读取并发布 X.com（Twitter）内容 |

### design/

本主题的技能产出视觉成品，而不是对已有工作的判断。核心是工艺：跳出最大概率的下一个 token，做出有明确主张的东西。

| Skill | 说明 |
|-------|------|
| [world-class-designer](./design/world-class-designer/) | 世界级工作室水准的界面设计与打磨，避免通用 AI 味：随机种子发散、盲审截图评审闭环、减法打磨、人工重写文案 |

### data/

| Skill | 说明 |
|-------|------|
| [fetch-device-data](./data/fetch-device-data/) | 按 HTTP 接口拉取设备非信号时序和信号波形：确认 base URL、设备与时间范围；数据项可用户指定或由 Agent 查目录获得（默认免 token）；信号为采集时刻 → 元数据 → 分页原始点 |

## 安装

用 [`skills`](https://skills.sh) CLI 安装。它读取本仓库，让你选择装哪些技能、装到哪些宿主，再写进各宿主的 skills 目录。

```bash
npx skills add gray0128/my-skills
```

加 `-g -y` 可跳过交互、直接全局安装。其他用法：

```bash
npx skills add gray0128/my-skills --list                                  # 先看仓库里有什么
npx skills add gray0128/my-skills --skill code-review --agent claude-code # 单个技能装到单个宿主
npx skills add gray0128/my-skills --skill '*' --agent '*' -g -y           # 全部技能装到全部已识别宿主
npx skills add ./ --skill x-com-post -g -y                                # 在本地克隆里安装
```

技能以自身目录名安装；上一层的主题目录只属于本仓库，不参与安装。

如果目标宿主不在 CLI 支持的范围内，直接把技能目录复制进该宿主的 skills 目录。本 README 中的 `<skill-dir>` 指技能最终落地的位置，例如 `~/.agents/skills/multi-agent-cli-dispatch`，执行命令前替换成真实路径。

安装 `brutal-advisor` 与 `world-class-designer`（单文件技能）：

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/gray0128/my-skills.git /tmp/my-skills
for skill in brutal-advisor world-class-designer; do
  cp -R "/tmp/my-skills/$skill" ~/.agents/skills/
done
```

## 使用

按宿主的既有方式调用技能：斜杠命令，或与技能 description 匹配的自然语言。

`x-com-post` —— `/x-com-post`，或“发推”、“post on x.com”、“获取推文”。

`code-review` —— `/code-review`，可附带目标与这段叠加要求：`/code-review 梳理一下这个 <TARGET> 的 skill，保持优雅的工程质量、良好的可维护性和极佳的用户体验。以重新定义问题为导向，运用第一性原理与MECE原则、量化思维，驱动开发与测试的系统性优化。`

`multi-agent-cli-dispatch` —— `/multi-agent-cli-dispatch <任务>`，或直接运行 dispatcher：

```bash
python3 <skill-dir>/scripts/dispatch.py \
  --workspace "$(pwd)" \
  --task '你的任务内容'
```

它能驱动的 CLI —— `claude`、`grok`、`reasonix`、`codebuddy`、`agy` —— 需在 `PATH` 中可用。注意这些是技能内部的分发目标，不是安装宿主。

## 依赖

### `x-com-post`

- [agent-browser](https://github.com/vercel-labs/agent-browser) CLI
- 已在目标用户配置中登录 X.com 的 Google Chrome
- macOS（预检脚本会检查 `~/Library/Application Support/Google/Chrome` 中的 Chrome Cookie）
- `scripts/preflight.sh` 必须保持可执行；如果是手动复制的，先跑 `chmod +x <skill-dir>/scripts/preflight.sh`

### `multi-agent-cli-dispatch`

- Python 3
- `PATH` 中至少一个：`claude`、`grok`、`reasonix`、`codebuddy`、`agy`
- 可选模型覆盖：把 `<skill-dir>` 下的 `agents.default.toml` 复制为旁边的 `agents.toml`。技能自带的 `.gitignore` 会忽略本地覆盖，不要提交。
