# my-skills

[English](./README.md) | [简体中文](./README-zh.md)

Personal agent skills, grouped into topic directories.

## Layout

| Directory | Scope |
|-----------|-------|
| [engineering/](./engineering/) | Judging software work, setting the rules it runs under, and delivering against them |
| [tools/](./tools/) | Driving external programs and platforms |
| [design/](./design/) | Designing interfaces that do not look machine-made |
| [data/](./data/) | Fetching domain data over HTTP |

Grouping is only a repository concern: each skill keeps its own directory name, so installing `engineering/code-review` yields a skill named `code-review`. Topics are open-ended — a new skill that fits none of them gets a new topic rather than a wrong one.

## Skills

### engineering/

The skills here act on the same things — code, PRs, issues, contracts — and differ in **how much they are allowed to change**. Pick by that first.

| Skill | Writes | Description |
|-------|--------|-------------|
| [brutal-advisor](./engineering/brutal-advisor/) | Chat reply | Unfiltered strategic advisor and cognitive mirror: root-cause and assumption audits, blind spots and opportunity cost, problem reframing, prioritized action plan |
| [code-review](./engineering/code-review/) | Chat reply | Strict maintainability review for abstraction quality, giant files, and spaghetti-condition growth; Grok Build `/code-review` (Cursor thermo-nuclear origin) |
| [pr-review](./engineering/pr-review/) | Platform review by default | Evidence-bound GitHub PR review workflow with current-head SHA binding |
| [analyze-review-conclusion](./engineering/analyze-review-conclusion/) | `评审报告分析采纳结论.md` | Turn review conclusions into adoption decisions verified against real project state |
| [audit-contract-governance](./engineering/audit-contract-governance/) | Chat reply, never files | Read-only, evidence-based audit of a repository's contract-governance system |
| [bootstrap-contract-governance](./engineering/bootstrap-contract-governance/) | Governance artifacts only | Install or migrate a minimal contract-governance system in an existing repository |
| [contract-first-delivery-loop](./engineering/contract-first-delivery-loop/) | In-scope code, contracts, tests, trackers | Execute one tracked, independently verifiable implementation slice under existing contracts |
| [issue-handler](./engineering/issue-handler/) | Code and a PR | Generic issue-to-PR workflow with plan comments and agent/model attribution, for GitHub, CNB, GitLab, Jira-backed repos, or similar trackers |

The last three form a governance suite split by mutation boundary rather than by phase: **audit** (read-only) → **bootstrap** (governance artifacts) → **delivery** (product changes under those contracts). It is not a mandatory pipeline — each can be invoked alone once its preconditions hold. Auditing and then fixing are two separate invocations; the fix does not inherit the audit's authorization.

### tools/

These skills operate someone else's execution environment. What the machine has installed, or which account the browser is logged into, is an environment dependency rather than a repository dependency — when it is missing the skill reports a classified failure instead of pretending to succeed.

| Skill | Description |
|-------|-------------|
| [multi-agent-cli-dispatch](./tools/multi-agent-cli-dispatch/) | Fan out one task to multiple coding-agent CLIs (`claude`, `grok`, `reasonix`, `codebuddy`, `agy`) with timeouts, logs, and result classification |
| [x-com-post](./tools/x-com-post/) | Read and publish on X.com (Twitter) via `agent-browser` with your Chrome profile |

### design/

These skills produce a visual artifact rather than a judgement about existing work. They are about craft — getting past the modal next-token answer into something with a point of view.

| Skill | Description |
|-------|-------------|
| [world-class-designer](./design/world-class-designer/) | Studio-grade UI design and polish without generic AI slop: seeded divergence, blind screenshot critic loop, subtractive polish, hand-written copy |

### data/

| Skill | Description |
|-------|-------------|
| [fetch-device-data](./data/fetch-device-data/) | Fetch device non-signal time series and signal waveforms over HTTP: confirm base URL, device, and time range; look up or use given KPIs (no token by default); signal path is timestamp → metadata → paged raw samples |

## Install

Install with the [`skills`](https://skills.sh) CLI. It reads this repository, lets you pick which skills and which hosts, and writes them into each host's skills directory.

```bash
npx skills add gray0128/my-skills
```

Add `-g -y` to skip the prompts and install globally. Other options:

```bash
npx skills add gray0128/my-skills --list                                  # see what the repository offers
npx skills add gray0128/my-skills --skill code-review --agent claude-code # one skill, one host
npx skills add gray0128/my-skills --skill '*' --agent '*' -g -y           # everything, every detected host
npx skills add ./ --skill x-com-post -g -y                                # from a local clone
```

A skill is installed under its own directory name; the topic directory above it is a repository concern and is never installed.

If your host is not one the CLI writes to, copy the skill directory itself into that host's skills directory. Throughout this README `<skill-dir>` means wherever a skill ended up, e.g. `~/.agents/skills/multi-agent-cli-dispatch`; substitute it before running a command.

For `brutal-advisor` and `world-class-designer` (single-file skills):

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/gray0128/my-skills.git /tmp/my-skills
for skill in brutal-advisor world-class-designer; do
  cp -R "/tmp/my-skills/$skill" ~/.agents/skills/
done
```

## Usage

Invoke a skill the way your host does: a slash command, or natural language that matches the skill's description.

`x-com-post` — `/x-com-post`, or "发推", "post on x.com", "获取推文".

`code-review` — `/code-review`, optionally with a target and this overlay: `/code-review 梳理一下这个 <TARGET> 的 skill，保持优雅的工程质量、良好的可维护性和极佳的用户体验。以重新定义问题为导向，运用第一性原理与MECE原则、量化思维，驱动开发与测试的系统性优化。`

`multi-agent-cli-dispatch` — `/multi-agent-cli-dispatch <task>`, or run the dispatcher directly:

```bash
python3 <skill-dir>/scripts/dispatch.py \
  --workspace "$(pwd)" \
  --task 'your task here'
```

The CLIs it can drive — `claude`, `grok`, `reasonix`, `codebuddy`, `agy` — must be on `PATH`. Note these are dispatch targets inside the skill, not install hosts.

## Requirements

### `x-com-post`

- [agent-browser](https://github.com/vercel-labs/agent-browser) CLI
- Google Chrome with an X.com login in the target profile
- macOS (preflight script checks Chrome cookies under `~/Library/Application Support/Google/Chrome`)
- `scripts/preflight.sh` must stay executable; if you copied the skill by hand, run `chmod +x <skill-dir>/scripts/preflight.sh`

### `multi-agent-cli-dispatch`

- Python 3
- One or more of: `claude`, `grok`, `reasonix`, `codebuddy`, `agy` on `PATH`
- Optional model overrides: copy `agents.default.toml` to `agents.toml` beside it in `<skill-dir>`. Local overrides are gitignored inside the skill; do not commit them.
