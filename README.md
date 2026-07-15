# my-skills

[English](./README.md) | [简体中文](./README-zh.md)

Personal agent skills.

## Skills

| Skill | Description |
|-------|-------------|
| [audit-contract-governance](./audit-contract-governance/) | Read-only, evidence-based audit of a repository's contract-governance system |
| [bootstrap-contract-governance](./bootstrap-contract-governance/) | Install or migrate a minimal contract-governance system in an existing repository |
| [contract-first-delivery-loop](./contract-first-delivery-loop/) | Execute one tracked, independently verifiable implementation slice under existing contracts |
| [contract-first-dev-loop](./contract-first-dev-loop/) | Combined contract-first, docs-driven development and governance loop |
| [issue-handler](./issue-handler/) | Generic issue-to-PR workflow with plan comments and agent/model attribution |
| [pr-review](./pr-review/) | Evidence-bound GitHub PR review workflow with current-head SHA binding |
| [x-com-post](./x-com-post/) | Read and publish on X.com (Twitter) via `agent-browser` with your Chrome profile |

## Install

Clone this repository and copy the skill you need into the relevant agent skills directory.

For `pr-review`:

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/gray0128/my-skills.git /tmp/my-skills
cp -R /tmp/my-skills/pr-review ~/.agents/skills/
```

For `issue-handler`:

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

For the contract-governance suite:

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

For `x-com-post`:

```bash
mkdir -p ~/.grok/skills
git clone https://github.com/gray0128/my-skills.git /tmp/my-skills
cp -R /tmp/my-skills/x-com-post ~/.grok/skills/
chmod +x ~/.grok/skills/x-com-post/scripts/preflight.sh
```

## Usage

After installing `x-com-post`, invoke in Grok:

- Slash command: `/x-com-post`
- Natural language: "发推", "post on x.com", "获取推文"

## Requirements

- [agent-browser](https://github.com/vercel-labs/agent-browser) CLI
- Google Chrome with an X.com login in the target profile
- macOS (preflight script checks Chrome cookies under `~/Library/Application Support/Google/Chrome`)
