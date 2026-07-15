# my-skills

[English](./README.md) | [简体中文](./README-zh.md)

个人 Agent Skills 集合。

## Skills

| Skill | 说明 |
|-------|------|
| [audit-contract-governance](./audit-contract-governance/) | 对仓库的契约治理体系执行只读、基于证据的审计 |
| [bootstrap-contract-governance](./bootstrap-contract-governance/) | 在现有仓库中安装或迁移最小化契约治理体系 |
| [contract-first-delivery-loop](./contract-first-delivery-loop/) | 在既有契约约束下执行一个已跟踪、可独立验证的实现切片 |
| [contract-first-dev-loop](./contract-first-dev-loop/) | 契约优先、文档驱动的开发与治理一体化闭环 |
| [issue-handler](./issue-handler/) | 通用的 Issue 到 PR 工作流，包含方案评论及 Agent/模型署名 |
| [multi-agent-cli-dispatch](./multi-agent-cli-dispatch/) | 将同一任务并行分发给多个编程 Agent CLI（`claude`、`grok`、`reasonix`、`codebuddy`、`agy`），并做超时、日志与结果分类 |
| [pr-review](./pr-review/) | 基于证据的 GitHub PR 评审工作流，绑定当前 HEAD SHA |
| [x-com-post](./x-com-post/) | 通过 `agent-browser` 和 Chrome 用户配置读取并发布 X.com（Twitter）内容 |

## 契约优先 skills 的迭代关系

`contract-first-dev-loop` 是最初的一体化 skill，在一个工作流中同时承担两类职责：安装或规范化项目治理体系，以及执行下一个已跟踪的开发切片。

其余三个 skill 是在此基础上的迭代升级，按照用户意图和修改权限边界拆分原有宽泛工作流：

| Skill | 在升级模型中的职责 | 对仓库的修改范围 |
|-------|--------------------|------------------|
| `audit-contract-governance` | 评估契约、跟踪器、指令和验证门禁是否一致，输出证据与缺口 | 只读 |
| `bootstrap-contract-governance` | 安装、迁移或修复最小可用的治理控制面 | 仅治理制品 |
| `contract-first-delivery-loop` | 在既有治理体系下交付一个已跟踪的实现成果 | 范围内的产品代码、契约、测试和跟踪器变更 |

这种升级是职责专业化，并不要求每次都依次运行三个 skill。常见的采用路径是 **审计 → 治理引导 → 交付**，但只要前置条件已经满足，每个 skill 都可以独立调用。

- 当紧凑、通用的统一入口比严格的模式分离更重要时，可以继续使用 `contract-first-dev-loop`。
- 需要更清晰的范围、更小的工作上下文、明确的写入权限或更安全的自动化时，优先使用升级后的三个 skill。
- `audit-contract-governance` 只负责诊断；若要修复审计发现的缺口，应明确切换到 `bootstrap-contract-governance`。
- 只有在权威契约和工作跟踪已经存在时，才使用 `contract-first-delivery-loop`。

## 安装

克隆本仓库，将所需 skill 复制到对应 Agent 的 skills 目录。

安装 `pr-review`：

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/gray0128/my-skills.git /tmp/my-skills
cp -R /tmp/my-skills/pr-review ~/.agents/skills/
```

安装 `issue-handler`：

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/gray0128/my-skills.git /tmp/my-skills
cp -R /tmp/my-skills/issue-handler ~/.agents/skills/
mkdir -p ~/.codex/skills ~/.gemini/skills ~/.grok/skills ~/.reasonix/skills ~/.claude/skills
ln -s ~/.agents/skills/issue-handler ~/.codex/skills/issue-handler
ln -s ~/.agents/skills/issue-handler ~/.gemini/skills/issue-handler
ln -s ~/.agents/skills/issue-handler ~/.grok/skills/issue-handler
ln -s ~/.agents/skills/issue-handler ~/.reasonix/skills/issue-handler
ln -s ~/.agents/skills/issue-handler ~/.claude/skills/issue-handler
```

安装契约治理 skill 套件：

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/gray0128/my-skills.git /tmp/my-skills
for skill in \
  contract-first-dev-loop \
  contract-first-delivery-loop \
  bootstrap-contract-governance \
  audit-contract-governance
do
  cp -R "/tmp/my-skills/$skill" ~/.agents/skills/
done
```

安装 `x-com-post`：

```bash
mkdir -p ~/.grok/skills
git clone https://github.com/gray0128/my-skills.git /tmp/my-skills
cp -R /tmp/my-skills/x-com-post ~/.grok/skills/
chmod +x ~/.grok/skills/x-com-post/scripts/preflight.sh
```

安装 `multi-agent-cli-dispatch`：

```bash
mkdir -p ~/.grok/skills
git clone https://github.com/gray0128/my-skills.git /tmp/my-skills
cp -R /tmp/my-skills/multi-agent-cli-dispatch ~/.grok/skills/
```

如需覆盖默认模型配置（本地 `agents.toml` 不会被仓库默认文件覆盖；skill 自带 `.gitignore` 忽略该文件）：

```bash
cp ~/.grok/skills/multi-agent-cli-dispatch/agents.default.toml \
   ~/.grok/skills/multi-agent-cli-dispatch/agents.toml
```

## 使用

安装 `x-com-post` 后，在 Grok 中调用：

- 斜杠命令：`/x-com-post`
- 自然语言："发推"、"post on x.com"、"获取推文"

安装 `multi-agent-cli-dispatch` 后，在 Grok 中调用：

- 斜杠命令：`/multi-agent-cli-dispatch <任务>`
- 或直接运行 dispatcher：

```bash
python3 ~/.grok/skills/multi-agent-cli-dispatch/scripts/dispatch.py \
  --workspace "$(pwd)" \
  --task '你的任务内容'
```

支持的 CLI：`claude`、`grok`、`reasonix`、`codebuddy`、`agy`（需在 `PATH` 中可用）。

## 依赖

### `x-com-post`

- [agent-browser](https://github.com/vercel-labs/agent-browser) CLI
- 已在目标用户配置中登录 X.com 的 Google Chrome
- macOS（预检脚本会检查 `~/Library/Application Support/Google/Chrome` 中的 Chrome Cookie）

### `multi-agent-cli-dispatch`

- Python 3
- `PATH` 中至少一个：`claude`、`grok`、`reasonix`、`codebuddy`、`agy`
