# Attribution Reference

## Purpose

When a dispatched task involves CNB or GitHub and may submit user-visible content, each CLI should append a different Agent/model footer to the final content.

This is configured per agent in `agents.default.toml` or `agents.toml`, similar to `model`.

## Per-Agent Field

```toml
[agents.claude]
content_footer = "agent：claudecode,model:minimax-m3"
```

Default bundled values:

| Agent | `content_footer` |
|---|---|
| `claude` | `agent：claudecode,model:minimax-m3` |
| `grok` | `agent：grok,model:grok4.5(high)` |
| `reasonix` | `agent：reasonix,model:deepseek-v4-pro` |
| `codebuddy` | `agent：codebuddy,model:HY3` |
| `agy` | `agent：antigravity,model:gemini-3.5-flash` |

## Auto Detection

`[attribution]` controls when the dispatcher appends the footer instruction:

```toml
[attribution]
enabled = true
auto_detect = true
task_patterns = [
  "cnb",
  "github",
  "cnb.cool",
  "github.com",
  "pulls/",
  "issues/",
]
instruction = """如需向 CNB/GitHub 提交任何用户可见内容（评论、评审、Issue/PR 说明等），请在内容最后一行原样附上：
{content_footer}"""
```

If the user task matches any `task_patterns`, each enabled agent receives its own footer instruction.

General tasks such as weather queries do not get attribution instructions.

## Runtime Overrides

Force attribution for a non-matching task:

```bash
--force-attribution
```

Disable attribution for one run:

```bash
--no-attribution
```

## Logs And Validation

When attribution applies, each agent log records:

```text
# content_footer: agent：claudecode,model:minimax-m3
```

If `--validate-cnb` is used and `--cnb-markers` is omitted, the dispatcher falls back to the selected agents' `content_footer` values for external validation.

## Footer Compatibility

Dispatch config uses compact footers such as `agent：claudecode,model:minimax-m3`.

The `cnb-pr-review` skill often emits `Agent：claudecode，Model：minimax-m3` instead. That is acceptable for human readers and for dispatch validation as long as the agent/model values stay identical.

Do not tell downstream CLIs to invent a different agent or model name. The attribution instruction now requires value fidelity while allowing label/casing variations.

## Validation Sources

CNB submissions may appear as either:

- Pull Review (`post-pull-review` → `list-pull-reviews`)
- Pull Comment (`post-pull-comment` → `list-pull-comments`)

Validation checks both endpoints so a successful comment-only review is not reported as missing.

## 变更记录

- 2026-07-09：grok 默认 attribution footer 更新为 `agent：grok,model:grok4.5(high)`。
