# my-skills

[English](./README.md) | [简体中文](./README-zh.md)

Personal agent skills, grouped into topic directories.

## Layout

| Directory | Scope |
|-----------|-------|
| [engineering/](./engineering/) | Judging plans, direction, and decisions without changing the work under review |
| [design/](./design/) | Designing interfaces that do not look machine-made |
| [data/](./data/) | Fetching domain data over HTTP |

Grouping is only a repository concern: each skill keeps its own directory name, so installing `engineering/brutal-advisor` yields a skill named `brutal-advisor`. Topics are open-ended — a new skill that fits none of them gets a new topic rather than a wrong one.

## Skills

### engineering/

This topic only judges. It pressure-tests a plan, direction, or decision and does not change the work under review.

| Skill | Writes | Description |
|-------|--------|-------------|
| [brutal-advisor](./engineering/brutal-advisor/) | Chat reply | Unfiltered strategic advisor and cognitive mirror: root-cause and assumption audits, blind spots and opportunity cost, problem reframing, prioritized action plan |

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
npx skills add gray0128/my-skills --skill brutal-advisor --agent claude-code # one skill, one host
npx skills add gray0128/my-skills --skill '*' --agent '*' -g -y           # everything, every detected host
npx skills add ./ --skill fetch-device-data -g -y                          # from a local clone
```

A skill is installed under its own directory name; the topic directory above it is a repository concern and is never installed.

If your host is not one the CLI writes to, copy the skill directory itself into that host's skills directory.

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
