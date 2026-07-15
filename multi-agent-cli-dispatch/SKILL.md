---
name: multi-agent-cli-dispatch
description: Dispatch one user-specified general task to multiple coding-agent CLIs in parallel with per-CLI model config, timeout handling, log capture, and result checks. Use when asked to run claude, grok, reasonix, codebuddy, and agy together; fan out the same task to several agent CLIs; monitor CLI completion; or orchestrate multi-agent CLI dispatch.
---

# Multi-Agent CLI Dispatch

Use this skill to fan out **one user-specified task** to multiple coding-agent CLIs in parallel, then verify whether each CLI actually finished that task.

Supported CLIs:

- `claude`
- `grok`
- `reasonix`
- `codebuddy`
- `agy`

## Task Contract

- The user provides the **full task body** every run.
- Treat the task as a **general instruction** by default.
- Downstream CLIs may use skills/workflows when helpful to complete the task.
- If the user names a specific skill such as `cnb-pr-review`, that skill is required; otherwise agents may choose tools/skills themselves.
- This dispatch skill itself must not expand scope (no unsolicited merges, extra issues, or repo-wide refactors beyond the user task).

## Configuration

Read config in this order:

1. `agents.default.toml` — bundled defaults
2. `agents.toml` — optional override in the same skill directory

Each agent block supports:

- `enabled`
- `model`
- `content_footer` — per-agent Agent/model line for CNB/GitHub user-visible submissions
- `args_before_task`
- `timeout_seconds`
- `require_task_hints`
- `min_body_chars`
- `success_patterns` / `failure_patterns`
- `workspace_args` / `workspace_bind_patterns` — optional conditional workspace binding (used by `agy`)
- `workspace_bind_exclude_patterns` — optional task patterns that suppress workspace binding even when `workspace_bind_patterns` match, used to avoid `agy --add-dir` derailment on explicit skill/platform review tasks
- `retry_on_derailment` / `retry_args_before_task` / `retry_task_prefix` — one-shot retry for known CLI derailment
- `retry_skip_task_patterns` — optional task patterns that must not be retried without workspace/tool access

`[attribution]` controls when footer instructions are auto-appended. Read `references/attribution.md` for details.

`[report_output]` controls when code-quality inspection tasks should write reports to per-agent directories, such as `docs/评审/grok/report.md`. PR review tasks are excluded by default.

Copy and customize models when needed:

```bash
cp .grok/skills/multi-agent-cli-dispatch/agents.default.toml \
   .grok/skills/multi-agent-cli-dispatch/agents.toml
```

Read `references/cli-invocation.md` before changing command shapes.

## Core Workflow

1. Confirm the exact task string from the user.
2. Resolve workspace directory (default: current project root).
3. Load `agents.default.toml` and optional `agents.toml`.
4. Verify each enabled CLI binary exists (`which <binary>`).
5. If the user only wants a subset, pass `--agents claude,reasonix`.
6. Run the dispatcher:

```bash
python3 .grok/skills/multi-agent-cli-dispatch/scripts/dispatch.py \
  --workspace "<absolute-workspace>" \
  --task '<user-task>'
```

7. Read `runs/<timestamp>/summary.md` and per-agent `*.log`.
8. Classify each agent as `success`, `ambiguous`, `failed`, or `timeout`.
9. Return a compact table plus follow-up actions for failed or ambiguous agents.

## Optional Flags

Run a subset:

```bash
python3 .grok/skills/multi-agent-cli-dispatch/scripts/dispatch.py \
  --workspace "<absolute-workspace>" \
  --agents claude,codebuddy \
  --task '<user-task>'
```

Override models for one run:

```bash
python3 .grok/skills/multi-agent-cli-dispatch/scripts/dispatch.py \
  --workspace "<absolute-workspace>" \
  --model-overrides '{"claude":"claude-opus-4-8[1m]","agy":"Gemini 3.5 Flash (High)"}' \
  --task '<user-task>'
```

Disable the default anti-derailment prefix:

```bash
python3 .grok/skills/multi-agent-cli-dispatch/scripts/dispatch.py \
  --workspace "<absolute-workspace>" \
  --no-task-prefix \
  --task '<user-task>'
```

Force or disable CNB/GitHub attribution footers:

```bash
python3 .grok/skills/multi-agent-cli-dispatch/scripts/dispatch.py \
  --workspace "<absolute-workspace>" \
  --force-attribution \
  --task '<user-task>'
```

## Result Interpretation

Treat completion in two default layers:

| Layer | Evidence | Meaning |
|---|---|---|
| Process | exit code, timeout, log file | CLI process ended |
| Output | task keywords, failure patterns, optional success patterns | Agent likely completed or derailed |

Use a third external layer only when the user task explicitly requires a side effect to verify, such as a CNB comment submission.

### Status rules

- `success`: exit code `0`, no failure pattern, enough task-hint hits (or a success pattern), and report file present when report_output applies
- `ambiguous`: exit code `0` but task keywords and success patterns are both missing
- `failed`: non-zero exit, failure pattern matched, response too short, or expected report file missing/empty
- `timeout`: process exceeded `timeout_seconds`
- `skipped`: disabled or unknown agent

Never report full success from exit code alone.

### Known CLI caveats

- `reasonix`: use `reasonix run`, not global `--yolo` before `run`
- `agy`: model flag must use equals form, e.g. `--model="Gemini 3.5 Flash (High)"`
- `agy`: builtin `antigravity_guide` often hijacks general tasks when it sees CLI flags like `--add-dir`; dispatcher now binds workspace only for repo/code tasks and retries once on derailment
- `agy`: do not retry explicit skill/CNB/GitHub submission tasks without workspace binding; if it derails on the first attempt, report `failed` instead of turning the retry into a no-tools refusal
- `agy`: do not pass `--print-timeout`, `--new-project`, or `--dangerously-skip-permissions` in dispatch config; mentioning CLI/skill names in the task prefix also increases derailment risk
- `agy`: has stricter derailment `failure_patterns`; treat its `failed` / `ambiguous` status as CLI-specific instability, not proof that other agents failed

## Optional External Validation

Run external validation only when the user explicitly asks for it in the task or via CLI flags.

Example for a CNB PR review task that the user wrote explicitly:

```bash
python3 .grok/skills/multi-agent-cli-dispatch/scripts/dispatch.py \
  --workspace "<absolute-workspace>" \
  --task '使用 skill "cnb-pr-review" 审核 PR https://cnb.cool/ifilfy/user-workbench/-/pulls/140' \
  --validate-cnb \
  --cnb-repo ifilfy/user-workbench \
  --cnb-pr 140
```

Attribution footers are auto-appended per agent from `content_footer`. If `--cnb-markers` is omitted, validation uses those footers.

`--validate-cnb` checks both CNB pull reviews and pull comments, and accepts normalized footer variants such as `Agent：reasonix，Model：deepseek-v4-pro` when the configured marker is `agent：reasonix,model:deepseek-v4-pro`. A comment visible on the PR page but missing from an older validation run usually means the agent used `post-pull-comment` or a footer format mismatch, not that the submission failed.

Default agent timeouts are 600 seconds (10 minutes). Dispatcher output is streamed live with an agent prefix while also being written to `runs/<timestamp>/<agent>.log`.

For code-quality inspection tasks that match `[report_output].task_patterns`, each agent is instructed to write its Markdown report to `<base_dir>/<agent>/<report_filename>` and the dispatcher creates that directory before launch. The default base directory is `docs/评审`; tasks matching `[report_output].exclude_task_patterns`, such as PR reviews, do not receive this report-output instruction.

## Reporting Template

```markdown
## Multi-Agent CLI Dispatch

- Task: <short excerpt>
- Workspace: <path>
- Run dir: <skill>/runs/<timestamp>

| Agent | Model | Status | Duration | Evidence | Notes |
|---|---|---|---:|---|---|
| claude | claude-opus-4-8[1m] | success | 27s | hints:上海,天气 | - |
| reasonix | deepseek-v4-pro | success | 13s | hints:上海,天气 | - |
| codebuddy | hy3 | success | 19s | hints:上海,天气 | - |
| grok | grok-4.5 | success | 22s | hints:上海,天气 | effort=high |
| agy | Gemini 3.5 Flash (High) | failed | 112s | derailment:--add-dir docs | skipped retry for explicit skill task |

### Follow-ups
- <only for failed/ambiguous agents>
```

Dispatcher `summary.md` also includes a compact `Notes` column for retry and classification reasons.

## Stop Conditions

Stop and report blocked when:

- No user task was provided
- Config file is missing or invalid
- All enabled CLIs are missing from `PATH`
- User asked for discussion only and explicitly said not to execute

The dispatcher skill itself should not expand task scope, merge PRs, or edit product code; it only launches CLIs and classifies results.

## Live Log Behaviour

The dispatcher streams per-agent output live while the CLI is still running and also writes it to `runs/<timestamp>/<agent>.log`. Two implementation details matter for diagnosing "log 看起来卡住" reports:

- Agent CLIs that print to a pipe (rather than a TTY) typically switch to fully-buffered I/O, which can hold back the first 4 KiB of output until the child exits. The dispatcher wraps each child with `stdbuf -oL -eL` on POSIX systems to force line buffering, so each newline reaches the dispatcher immediately. On systems without `stdbuf`, the dispatcher falls back to the previous behaviour and the same buffering caveat applies.
- If no new line has been received for 15 seconds, the dispatcher emits a heartbeat comment of the form `# ... still running (Ns, no output yet)` to both the live prefix and the log file, so a silent agent can be distinguished from a stuck one. The heartbeat is informational and does not affect classification.

## Changelog

- v1.5 — 2026-07-09
  - 默认与各 agent `timeout_seconds` 由 360（6 分钟）调整为 600（10 分钟）。

- v1.4 — 2026-07-09
  - 默认 `task_prefix` 移除“否则不要自行引入其他 workflow 或 skill”，允许 agent 按需自主使用 skill/workflow。
  - 收紧 `extract_task_hints`：过滤 URL 噪声与通用动词；≥4 个 hint 时需至少命中 2 个才算 task signal。
  - 全局 `general_failure_patterns` 去掉 bare `error:` / `错误：`，降低代码审查正文误杀。
  - report_output 任务在结束后校验报告文件存在且非空，否则降为 `failed`。
  - `summary.md` / `summary.json` 记录每 agent 的 `model`；stdbuf 包装信息不再写入 Notes。
  - 新增 `.gitignore` 忽略 `runs/` 与本地 `agents.toml`。

- v1.3 — 2026-07-09
  - grok 默认模型改为 `grok-4.5`，并固定 `--effort high`（grok4.5(high)）。
  - 同步更新 attribution footer 为 `agent：grok,model:grok4.5(high)`，以及 cli-invocation / attribution 文档。

- v1.2 — 2026-07-08 23:08:12
  - Wrap each agent child with `stdbuf -oL -eL` to force line buffering and keep the live log streaming.
  - Emit a 15-second heartbeat line while a child is silent so users can distinguish "still working" from "hung".
  - Harden `signal_process_group` to fall back to `proc.send_signal` when `killpg` is denied (e.g. CI sandboxes).
  - Capture per-thread exceptions in the dispatch pool instead of aborting the run.
