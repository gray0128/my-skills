# CLI Invocation Reference

These shapes are validated for general-task dispatch. Keep them aligned with `agents.default.toml`.

The dispatcher forwards the user task verbatim, plus an optional short anti-derailment prefix. If the user wants a specific skill, they must name it in the task text.

## claude

```bash
claude -p \
  --model 'claude-opus-4-8[1m]' \
  --dangerously-skip-permissions \
  '<task>'
```

- Default model: `claude-opus-4-8[1m]`
- Default timeout: `600` seconds
- Non-interactive mode: `-p` / `--print`

## grok

```bash
grok \
  -m grok-4.5 \
  --effort high \
  --permission-mode bypassPermissions \
  --cwd '<workspace>' \
  -p '<task>'
```

- Config model id: `grok-4.5` with `--effort high` (grok4.5(high))
- Non-interactive mode: `-p` / `--single`
- Attribution footer default: `agent：grok,model:grok4.5(high)`
- Dispatcher streams grok output live, which makes proxy retries such as `HTTP 502 Bad Gateway` visible before the process exits.

## reasonix

```bash
reasonix run \
  --model deepseek-v4-pro \
  --dir '<workspace>' \
  '<task>'
```

- Default model: `deepseek-v4-pro`
- Do **not** invoke `reasonix --yolo run ...`; global `--yolo` can fail with TTY errors in non-interactive environments
- Prefer `reasonix run` for one-shot tasks

## codebuddy

```bash
codebuddy -p \
  --model hy3 \
  --dangerously-skip-permissions \
  '<task>'
```

- Default model: `hy3`
- Non-interactive mode: `-p` / `--print`

## agy

General task (default):

```bash
agy --print \
  --model="Gemini 3.5 Flash (High)" \
  '<task>'
```

Repo/code task (workspace bind enabled by `workspace_bind_patterns`):

```bash
agy --print \
  --model="Gemini 3.5 Flash (High)" \
  --add-dir '<workspace>' \
  '<task>'
```

- Default model: `Gemini 3.5 Flash (High)`
- **Required**: `model_flag_style = "equals"` because the display name contains spaces
- **Derailment root cause**: builtin `antigravity_guide` treats CLI flags such as `--add-dir` as the user question and explains them instead of running the task
- **Do not pass** `--print-timeout` in dispatch; the flag name itself can become the interpreted prompt. Use dispatcher `timeout_seconds` instead
- **Mitigation**: only append `--add-dir` when the task matches `workspace_bind_patterns`; use an agy-specific task prefix that does **not** mention CLI/skill/workflow; retry once without workspace bind on derailment
- **Explicit skill/platform review tasks**: `workspace_bind_exclude_patterns` suppresses `--add-dir` for prompts such as `使用 skill "cnb-pr-review" 审核 PR ...`; dispatcher still runs with cwd set to the workspace, but avoids triggering `antigravity_guide` on the CLI flag itself
- **Do not retry** explicit skill/platform-submission tasks without workspace binding. If agy derails on a task such as `使用 skill "cnb-pr-review" 审核 PR ...`, report that agy failed instead of retrying with a no-tools prompt; the retry can otherwise turn into a refusal that still echoes enough task keywords to look successful.
- **Failure classification** must include agy refusal phrases such as being unable to access/review the PR or lacking the requested skill. Task keyword matches alone are not enough evidence for agy success.
- **Avoid**: `--new-project` in dispatch; agy may treat it as the primary task and explore the repo instead
- **Avoid**: `--dangerously-skip-permissions` in non-interactive dispatch; the flag name can trigger meta replies about CLI flags
- Available models come from `agy models`
- Dispatcher cwd is already set to `<workspace>`; general Q&A tasks do not need `--add-dir`

## Model Override File

Edit `agents.toml`:

```toml
[agents.claude]
model = "claude-opus-4-8[1m]"

[agents.grok]
model = "grok-4.5"

[agents.reasonix]
model = "deepseek-v4-pro"

[agents.codebuddy]
model = "hy3"

[agents.agy]
model = "Gemini 3.5 Flash (High)"
```

One-run overrides can also be passed to `dispatch.py` via `--model-overrides`.

## 变更记录

- 2026-07-09：默认超时由 360 秒调整为 600 秒（10 分钟）。
- 2026-07-09：grok 默认模型更新为 `grok-4.5` + `--effort high`（grok4.5(high)），同步示例与 attribution footer。
