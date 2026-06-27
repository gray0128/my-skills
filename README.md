# my-skills

Personal agent skills.

## Skills

| Skill | Description |
|-------|-------------|
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
