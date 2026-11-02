# Validation Reference

## Layer 1: Process

Recorded by `scripts/dispatch.py`:

- start / end timestamps
- per-agent timeout from config
- exit code
- live stdout/stderr stream in dispatcher output
- full stdout/stderr log at `runs/<timestamp>/<agent>.log`

Timeout defaults to `600` seconds (10 minutes) unless overridden per agent.

## Layer 2: General Task Output

Configured globally and per agent in TOML:

- `defaults.require_task_hints`: when `true`, response body should contain keywords extracted from the user task
- `defaults.min_body_chars`: reject very short responses as failed
- `defaults.general_failure_patterns`: shared **strong** process/CLI failure signals only (no bare `error:`)
- `failure_patterns`: agent-specific derailment signals (matched case-insensitively for ASCII patterns)
- `success_patterns`: optional explicit success signals for specialized tasks
- `workspace_bind_patterns`: only append `workspace_args` such as `--add-dir` when the user task needs repo access
- `retry_on_derailment`: one automatic retry for agents such as `agy` when derailment is detected
- report-output tasks: after classification, the expected `report.md` must exist and be non-empty or status becomes `failed`

Classification order:

1. non-zero exit or timeout
2. failure / derailment patterns
3. `min_body_chars`
4. configured `success_patterns`, or task-hint match when `require_task_hints = true`
5. report-file presence check (when report_output applied)
6. otherwise `ambiguous`

For general tasks, task-hint matching is the primary success signal. Hints drop URL noise (`https`, host crumbs, `pulls`) and generic verbs (`使用`, `skill`). When 4+ hints are extracted, at least **two** must appear in the body.

Examples:

- task: `查询上海今日天气` -> hints like `上海`, `天气`
- task: `总结 README 的部署步骤` -> hints like `README`, `部署`
- task: `使用 skill "cnb-pr-review" 审核 PR https://cnb.cool/.../pulls/145` -> `cnb-pr-review`, `审核`, `145`, repo segments (not `https`/`cool`)

Log analysis ignores the dispatcher header (`# command`, `# started`, `# user_task`) and inspects only the agent body.

## Layer 3: Optional External Validation

Use only when the user task explicitly requires proof of an external side effect.

The dispatcher supports CNB review verification via `--validate-cnb`, but that is not part of the default general-task flow. Enable it only when the user wrote a CNB-related task or asked for external proof.

When `--cnb-markers` is omitted, validation falls back to the selected agents' `content_footer` values from `agents.default.toml`.

CNB validation queries both `list-pull-reviews` and `list-pull-comments`, because some CLIs submit PR reviews while others submit PR comments. A visible page comment that is missing from validation usually means it landed in the comments API, not the reviews API.

Footer matching uses two layers:

1. `exact`: configured `content_footer` appears verbatim in the submission body
2. `normalized`: the last footer line matches after normalizing `Agent/agent`、`Model/model` labels, comma style, and case on the configured agent/model values

This keeps validation compatible with `cnb-pr-review`, which often emits `Agent：reasonix，Model：deepseek-v4-pro` even when dispatch config expects `agent：reasonix,model:deepseek-v4-pro`.

The summary reports `unmatched_markers` for configured footers with no review/comment match in the run window.

## Dispatcher Exit Codes

- `0`: all started agents ended in `success`
- `2`: no hard failures, but at least one agent is `ambiguous`
- `1`: at least one agent `failed` or `timeout`

## Recommended Reporting

Always include:

- per-agent status
- model used
- log path
- task-hint hits and failure-pattern hits
- external validation only when explicitly requested

Never equate "CLI exited" with "user task completed".

## 变更记录

- 2026-07-09：默认超时由 360 秒调整为 600 秒（10 分钟）。
- 2026-07-09：收紧 task-hint 提取与命中门槛；全局 failure 去掉 bare `error:` 误杀；report 落盘校验；summary 增加 Model 列。
