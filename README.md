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

## Evolution of the contract-first skills

`contract-first-dev-loop` is the original all-in-one skill. It combines two responsibilities in one workflow: installing or formalizing project governance and executing the next tracked development slice.

The other three skills are an iterative upgrade that separates this broad workflow by user intent and mutation boundary:

| Skill | Role in the upgraded model | Repository changes |
|-------|----------------------------|--------------------|
| `audit-contract-governance` | Assess whether contracts, trackers, instructions, and verification gates are coherent; report evidence and gaps | Read-only |
| `bootstrap-contract-governance` | Install, migrate, or repair the smallest useful governance control surface | Governance artifacts only |
| `contract-first-delivery-loop` | Deliver one tracked implementation outcome under an existing governance system | In-scope product, contract, test, and tracker changes |

This is a specialization, not a mandatory three-step pipeline. A common adoption path is **audit → bootstrap → delivery**, but each skill can be invoked independently when its preconditions already hold.

- Keep using `contract-first-dev-loop` when a compact, general-purpose entry point is more useful than strict mode separation.
- Prefer the upgraded skills when you need clearer scope, smaller working context, explicit write authority, or safer automation.
- Use `audit-contract-governance` for diagnosis only; move to `bootstrap-contract-governance` explicitly if the reported gaps should be fixed.
- Use `contract-first-delivery-loop` only after authoritative contracts and work tracking already exist.

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
