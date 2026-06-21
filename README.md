# my-skills

Personal [Grok](https://grok.com) agent skills.

## Skills

| Skill | Description |
|-------|-------------|
| [x-com-post](./x-com-post/) | Read and publish on X.com (Twitter) via `agent-browser` with your Chrome profile |

## Install

Clone a skill into your Grok user skills directory:

```bash
mkdir -p ~/.grok/skills
git clone https://github.com/gray0128/my-skills.git /tmp/my-skills
cp -R /tmp/my-skills/x-com-post ~/.grok/skills/
chmod +x ~/.grok/skills/x-com-post/scripts/preflight.sh
```

## Usage

After install, invoke in Grok:

- Slash command: `/x-com-post`
- Natural language: "发推", "post on x.com", "获取推文"

## Requirements

- [agent-browser](https://github.com/vercel-labs/agent-browser) CLI
- Google Chrome with an X.com login in the target profile
- macOS (preflight script checks Chrome cookies under `~/Library/Application Support/Google/Chrome`)