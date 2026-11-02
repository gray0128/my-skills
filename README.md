# my-skills

[English](./README.md) | [简体中文](./README-zh.md)

Personal agent skills.

## Skills


| Skill | Platform | Description |
|-------|----------|-------------|
| [issue-handler](./issue-handler/) | GitHub | Generic issue-to-PR workflow with plan comments and agent/model attribution |
| [pr-review](./pr-review/) | GitHub | Evidence-bound GitHub PR review workflow with current-head SHA binding |


### General skills

| Skill | Description |
|-------|-------------|
| [analyze-review-conclusion](./analyze-review-conclusion/) | Turn review conclusions into adoption decisions verified against real project state, and generate `评审报告分析采纳结论.md` |
| [audit-contract-governance](./audit-contract-governance/) | Read-only, evidence-based audit of a repository's contract-governance system |
| [bootstrap-contract-governance](./bootstrap-contract-governance/) | Install or migrate a minimal contract-governance system in an existing repository |
| [brutal-advisor](./brutal-advisor/) | Unfiltered strategic advisor and cognitive mirror: root-cause and assumption audits, blind spots and opportunity cost, problem reframing, prioritized action plan |
| [code-review](./code-review/) | Strict maintainability review for abstraction quality, giant files, and spaghetti-condition growth; Grok Build `/code-review` (Cursor thermo-nuclear origin) |
| [contract-first-delivery-loop](./contract-first-delivery-loop/) | Execute one tracked, independently verifiable implementation slice under existing contracts |
| [multi-agent-cli-dispatch](./multi-agent-cli-dispatch/) | Fan out one task to multiple coding-agent CLIs (`claude`, `grok`, `reasonix`, `codebuddy`, `agy`) with timeouts, logs, and result classification |
| [world-class-designer](./world-class-designer/) | Studio-grade UI design and polish without generic AI slop: seeded divergence, blind screenshot critic loop, subtractive polish, hand-written copy |
| [x-com-post](./x-com-post/) | Read and publish on X.com (Twitter) via `agent-browser` with your Chrome profile |
| [fetch-device-data](./fetch-device-data/) | Fetch device non-signal time series and signal waveforms over HTTP: confirm base URL, device, time range, and token; list or select KPIs; signal path is timestamp → metadata → paged raw samples |

## Contract-governance skills

The contract-governance suite separates workflows by user intent and mutation boundary:

| Skill | Role in the upgraded model | Repository changes |
|-------|----------------------------|--------------------|
| `audit-contract-governance` | Assess whether contracts, trackers, instructions, and verification gates are coherent; report evidence and gaps | Read-only |
| `bootstrap-contract-governance` | Install, migrate, or repair the smallest useful governance control surface | Governance artifacts only |
| `contract-first-delivery-loop` | Deliver one tracked implementation outcome under an existing governance system | In-scope product, contract, test, and tracker changes |

The suite is not a mandatory three-step pipeline. A common adoption path is **audit → bootstrap → delivery**, but each skill can be invoked independently when its preconditions already hold.

- Use `audit-contract-governance` for diagnosis only; move to `bootstrap-contract-governance` explicitly if the reported gaps should be fixed.
- Use `bootstrap-contract-governance` to establish or repair authoritative governance artifacts without implementing product features.
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
  contract-first-delivery-loop \
  bootstrap-contract-governance \
  audit-contract-governance
do
  cp -R "/tmp/my-skills/$skill" ~/.agents/skills/
done
```

For `code-review`:

```bash
mkdir -p ~/.agents/skills ~/.grok/skills ~/.claude/skills ~/.codex/skills
git clone https://github.com/gray0128/my-skills.git /tmp/my-skills
cp -R /tmp/my-skills/code-review ~/.agents/skills/
ln -s ~/.agents/skills/code-review ~/.grok/skills/code-review
ln -s ~/.agents/skills/code-review ~/.claude/skills/code-review
ln -s ~/.agents/skills/code-review ~/.codex/skills/code-review
```

For `x-com-post`:

```bash
mkdir -p ~/.grok/skills
git clone https://github.com/gray0128/my-skills.git /tmp/my-skills
cp -R /tmp/my-skills/x-com-post ~/.grok/skills/
chmod +x ~/.grok/skills/x-com-post/scripts/preflight.sh
```

For `multi-agent-cli-dispatch`:

```bash
mkdir -p ~/.grok/skills
git clone https://github.com/gray0128/my-skills.git /tmp/my-skills
cp -R /tmp/my-skills/multi-agent-cli-dispatch ~/.grok/skills/
```

Optional model overrides (do not commit local overrides if you keep them in-repo elsewhere):

```bash
cp ~/.grok/skills/multi-agent-cli-dispatch/agents.default.toml \
   ~/.grok/skills/multi-agent-cli-dispatch/agents.toml
```

For `brutal-advisor` and `world-class-designer` (single-file skills):

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/gray0128/my-skills.git /tmp/my-skills
for skill in brutal-advisor world-class-designer; do
  cp -R "/tmp/my-skills/$skill" ~/.agents/skills/
done
```

## Usage

After installing `x-com-post`, invoke in Grok:

- Slash command: `/x-com-post`
- Natural language: "发推", "post on x.com", "获取推文"

After installing `multi-agent-cli-dispatch`, invoke in Grok:

- Slash command: `/multi-agent-cli-dispatch <task>`
- Or run the dispatcher directly:

```bash
python3 ~/.grok/skills/multi-agent-cli-dispatch/scripts/dispatch.py \
  --workspace "$(pwd)" \
  --task 'your task here'
```

Supported CLIs: `claude`, `grok`, `reasonix`, `codebuddy`, `agy` (must be on `PATH`).

After installing `code-review`, invoke:

- Slash command: `/code-review`
- Example overlay: `/code-review 梳理一下这个 <TARGET> 的 skill，保持优雅的工程质量、良好的可维护性和极佳的用户体验。以重新定义问题为导向，运用第一性原理与MECE原则、量化思维，驱动开发与测试的系统性优化。`

## Requirements

### `x-com-post`

- [agent-browser](https://github.com/vercel-labs/agent-browser) CLI
- Google Chrome with an X.com login in the target profile
- macOS (preflight script checks Chrome cookies under `~/Library/Application Support/Google/Chrome`)

### `multi-agent-cli-dispatch`

- Python 3
- One or more of: `claude`, `grok`, `reasonix`, `codebuddy`, `agy` on `PATH`
