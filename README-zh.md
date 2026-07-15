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
| [pr-review](./pr-review/) | 基于证据的 GitHub PR 评审工作流，绑定当前 HEAD SHA |
| [x-com-post](./x-com-post/) | 通过 `agent-browser` 和 Chrome 用户配置读取并发布 X.com（Twitter）内容 |

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

## 使用

安装 `x-com-post` 后，在 Grok 中调用：

- 斜杠命令：`/x-com-post`
- 自然语言："发推"、"post on x.com"、"获取推文"

## 依赖

- [agent-browser](https://github.com/vercel-labs/agent-browser) CLI
- 已在目标用户配置中登录 X.com 的 Google Chrome
- macOS（预检脚本会检查 `~/Library/Application Support/Google/Chrome` 中的 Chrome Cookie）
