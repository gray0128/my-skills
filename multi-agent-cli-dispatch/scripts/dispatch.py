#!/usr/bin/env python3
"""Dispatch one task to multiple coding-agent CLIs in parallel."""

from __future__ import annotations

import argparse
import json
import os
import re
import select
import signal
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PRINT_LOCK = threading.Lock()


def load_toml(path: Path) -> dict[str, Any]:
    try:
        import tomllib  # py3.11+
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore

    with path.open("rb") as fh:
        return tomllib.load(fh)


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def load_config(skill_dir: Path) -> dict[str, Any]:
    default_path = skill_dir / "agents.default.toml"
    custom_path = skill_dir / "agents.toml"
    config = load_toml(default_path)
    if custom_path.exists():
        config = deep_merge(config, load_toml(custom_path))
    return config


def expand_args(args: list[str], workspace: str) -> list[str]:
    return [workspace if item == "{workspace}" else item for item in args]


def task_matches_patterns(task: str, patterns: list[str]) -> bool:
    haystack = task.casefold()
    for pattern in patterns:
        token = str(pattern).strip()
        if not token:
            continue
        if re.search(token, haystack, re.IGNORECASE):
            return True
    return False


def pattern_matches(body: str, pattern: str) -> bool:
    if pattern.isascii():
        return pattern.casefold() in body.casefold()
    return pattern in body


def resolve_args_before_task(agent_cfg: dict[str, Any], workspace: str, user_task: str) -> list[str]:
    if "retry_args_before_task" in agent_cfg and agent_cfg.get("_force_retry_args"):
        return expand_args(agent_cfg["retry_args_before_task"], workspace)

    args = expand_args(agent_cfg.get("args_before_task", []), workspace)
    workspace_args = agent_cfg.get("workspace_args")
    if workspace_args is None:
        return args

    patterns = agent_cfg.get("workspace_bind_patterns", [])
    exclude_patterns = agent_cfg.get("workspace_bind_exclude_patterns", [])
    if exclude_patterns and task_matches_patterns(user_task, exclude_patterns):
        return args
    if patterns and task_matches_patterns(user_task, patterns):
        return args + expand_args(workspace_args, workspace)
    return args


def should_retry_for_derailment(
    result: AgentResult,
    user_task: str,
    agent_cfg: dict[str, Any],
    defaults: dict[str, Any],
) -> bool:
    if result.timed_out or not agent_cfg.get("retry_on_derailment"):
        return False
    require_task_hints = bool(agent_setting(agent_cfg, defaults, "require_task_hints", False))
    retry_candidate = bool(result.failure_pattern_hits) or (
        result.status == "ambiguous" and require_task_hints and not result.task_hint_hits
    )
    if not retry_candidate:
        return False
    retry_skip_patterns = agent_cfg.get("retry_skip_task_patterns", [])
    if retry_skip_patterns and task_matches_patterns(user_task, retry_skip_patterns):
        result.notes.append("Skipping derailment retry because task requires explicit tools/skills.")
        return False
    return True


def task_involves_platform_submission(user_task: str, attribution_cfg: dict[str, Any]) -> bool:
    haystack = user_task.casefold()
    for pattern in attribution_cfg.get("task_patterns", []):
        if str(pattern).casefold() in haystack:
            return True
    return False


def apply_attribution(
    user_task: str,
    agent_cfg: dict[str, Any],
    attribution_cfg: dict[str, Any],
    *,
    force: bool = False,
    disabled: bool = False,
) -> tuple[str, str | None]:
    if disabled or not attribution_cfg.get("enabled", True):
        return user_task, None

    content_footer = str(agent_cfg.get("content_footer", "")).strip()
    if not content_footer:
        return user_task, None

    should_apply = force or (
        attribution_cfg.get("auto_detect", True)
        and task_involves_platform_submission(user_task, attribution_cfg)
    )
    if not should_apply:
        return user_task, None

    template = attribution_cfg.get(
        "instruction",
        "如需向 CNB/GitHub 提交任何用户可见内容，请在内容最后一行原样附上：\n{content_footer}",
    )
    instruction = str(template).format(content_footer=content_footer)
    return f"{user_task.strip()}\n\n{instruction.strip()}", content_footer


def resolve_report_dir(workspace: str, base_dir: str, agent_name: str) -> Path:
    base_path = Path(base_dir)
    if not base_path.is_absolute():
        base_path = Path(workspace) / base_path
    return base_path / agent_name


def apply_report_output(
    user_task: str,
    report_cfg: dict[str, Any],
    agent_name: str,
    workspace: str,
) -> tuple[str, str | None]:
    """Return (task, report_file_path). report_file_path is set when instruction applies."""
    if not report_cfg.get("enabled", False):
        return user_task, None

    include_patterns = report_cfg.get("task_patterns", [])
    if include_patterns and not task_matches_patterns(user_task, include_patterns):
        return user_task, None

    exclude_patterns = report_cfg.get("exclude_task_patterns", [])
    if exclude_patterns and task_matches_patterns(user_task, exclude_patterns):
        return user_task, None

    base_dir = str(report_cfg.get("base_dir", "")).strip()
    if not base_dir:
        return user_task, None

    report_dir = resolve_report_dir(workspace, base_dir, agent_name)
    report_file = report_dir / str(report_cfg.get("report_filename", "report.md")).strip()
    template = report_cfg.get(
        "instruction",
        "请将报告写入以下路径：\n{report_file}",
    )
    instruction = str(template).format(
        agent_name=agent_name,
        report_dir=str(report_dir),
        report_file=str(report_file),
    )
    return f"{user_task.strip()}\n\n{instruction.strip()}", str(report_file)


def prepare_task(user_task: str, defaults: dict[str, Any], agent_cfg: dict[str, Any]) -> str:
    if agent_cfg.get("apply_task_prefix") is False:
        return user_task
    if defaults.get("apply_task_prefix") is False:
        return user_task
    if agent_cfg.get("_force_retry_prefix"):
        prefix = agent_cfg.get("retry_task_prefix") or agent_cfg.get("task_prefix") or defaults.get("task_prefix", "")
    else:
        prefix = agent_cfg.get("task_prefix") or defaults.get("task_prefix", "")
    if not prefix:
        return user_task
    return f"{prefix.strip()}\n\n{user_task.strip()}"


def format_command_for_log(command: list[str]) -> str:
    return " ".join(part.replace("\n", "\\n") for part in command)


def log_body(output: str) -> str:
    lines = output.splitlines()
    body_start = 0
    for idx, line in enumerate(lines):
        if line.startswith("# user_task:"):
            body_start = idx + 1
            break
    while body_start < len(lines) and not lines[body_start].strip():
        body_start += 1
    return "\n".join(lines[body_start:]).strip()


# Noise tokens that appear in almost every URL / instruction task and must not
# alone drive a "success" classification.
HINT_STOPWORDS = frozenset(
    {
        "https",
        "http",
        "www",
        "com",
        "org",
        "net",
        "cool",
        "html",
        "htm",
        "using",
        "with",
        "from",
        "this",
        "that",
        "please",
        "task",
        "user",
        "agent",
        "model",
        "pull",
        "pulls",
        "issues",
        "issue",
        "path",
        "file",
        "only",
        "just",
        "then",
        "when",
        "where",
        "what",
        "your",
        "have",
        "will",
        "must",
        "need",
        "into",
        "over",
        "under",
        "about",
        "skill",
        "使用",
        "请做",
        "请对",
        "进行",
        "完成",
        "任务",
        "用户",
        "下面",
        "以及",
        "或者",
        "根据",
        "说明",
        "执行",
    }
)


def _is_useful_hint(token: str) -> bool:
    value = token.strip()
    if len(value) < 2:
        return False
    if value.casefold() in HINT_STOPWORDS:
        return False
    if re.fullmatch(r"\d+", value) and len(value) < 2:
        return False
    return True


def extract_task_hints(task: str) -> list[str]:
    """Extract discriminative keywords from the user task for output checks.

    Prefer repo names, PR/issue numbers, skill ids, and domain words. Drop URL
    scheme/host crumbs and generic instruction verbs that caused false success.
    """
    hints: list[str] = []

    def add_hint(value: str) -> None:
        token = value.strip().strip("\"'`“”‘’")
        if not _is_useful_hint(token):
            return
        if token not in hints:
            hints.append(token)

    # PR / issue numbers from platform URLs or shorthand.
    for match in re.finditer(r"(?i)(?:pulls?|issues?|pr|issue)[#/\s-]*(\d{1,6})\b", task):
        add_hint(match.group(1))

    # Meaningful path segments from URLs (skip scheme/host noise).
    for url in re.findall(r"https?://[^\s)>\]]+", task):
        path = re.sub(r"^https?://", "", url, flags=re.IGNORECASE)
        for part in re.split(r"[/?#&=._-]+", path):
            if len(part) >= 3 and part.casefold() not in HINT_STOPWORDS:
                add_hint(part)

    # Quoted identifiers (skill names, file paths fragments).
    for match in re.finditer(r"[\"'`“”]([^\"'`“”]{2,64})[\"'`“”]", task):
        quoted = match.group(1).strip()
        add_hint(quoted)
        for piece in re.split(r"[/\\.\s]+", quoted):
            add_hint(piece)

    for chunk in re.split(r"[\s，。；、！？,.;!?：:（）()【】\[\]<>]+", task):
        if chunk.startswith("http://") or chunk.startswith("https://"):
            continue
        for token in re.findall(r"[\u4e00-\u9fff]{2,8}|[A-Za-z][A-Za-z0-9_-]{2,}|\d{2,}", chunk):
            if len(token) > 8 and re.fullmatch(r"[\u4e00-\u9fff]+", token):
                # Keep ends of long Chinese phrases; avoid flooding with bigrams.
                add_hint(token[:4])
                add_hint(token[-4:])
            else:
                add_hint(token)
    return hints[:12]


def enough_task_hint_hits(hits: list[str], all_hints: list[str]) -> bool:
    """Require more than one hit when the task yields several strong hints."""
    if not hits:
        return False
    if len(all_hints) >= 4:
        return len(hits) >= 2
    return True


def collect_patterns(agent_cfg: dict[str, Any], defaults: dict[str, Any], key: str) -> list[str]:
    general_key = f"general_{key}"
    patterns = list(defaults.get(general_key, defaults.get(key, [])))
    for pattern in agent_cfg.get(key, []):
        if pattern not in patterns:
            patterns.append(pattern)
    return patterns


def agent_setting(agent_cfg: dict[str, Any], defaults: dict[str, Any], key: str, default: Any = None) -> Any:
    if key in agent_cfg:
        return agent_cfg[key]
    if key in defaults:
        return defaults[key]
    return default


def build_command(
    agent_cfg: dict[str, Any],
    model: str,
    workspace: str,
    user_task: str,
    task: str,
) -> list[str]:
    binary = agent_cfg["binary"]
    cmd: list[str] = [binary]
    subcommand = agent_cfg.get("subcommand")
    if subcommand:
        cmd.append(subcommand)

    model_flag = agent_cfg.get("model_flag", "--model")
    style = agent_cfg.get("model_flag_style", "space")
    if style == "equals":
        cmd.append(f"{model_flag}={model}")
    else:
        cmd.extend([model_flag, model])

    cmd.extend(resolve_args_before_task(agent_cfg, workspace, user_task))
    cmd.append(task)
    return cmd


@dataclass
class AgentResult:
    name: str
    enabled: bool
    model: str = ""
    started: bool = False
    finished: bool = False
    exit_code: int | None = None
    timed_out: bool = False
    duration_seconds: float = 0.0
    command: list[str] = field(default_factory=list)
    log_path: str = ""
    report_file: str | None = None
    success_pattern_hits: list[str] = field(default_factory=list)
    failure_pattern_hits: list[str] = field(default_factory=list)
    task_hint_hits: list[str] = field(default_factory=list)
    content_footer: str | None = None
    output_excerpt: str = ""
    status: str = "pending"  # pending|skipped|running|success|failed|timeout|ambiguous
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "enabled": self.enabled,
            "model": self.model,
            "started": self.started,
            "finished": self.finished,
            "exit_code": self.exit_code,
            "timed_out": self.timed_out,
            "duration_seconds": round(self.duration_seconds, 2),
            "command": self.command,
            "log_path": self.log_path,
            "report_file": self.report_file,
            "success_pattern_hits": self.success_pattern_hits,
            "failure_pattern_hits": self.failure_pattern_hits,
            "task_hint_hits": self.task_hint_hits,
            "content_footer": self.content_footer,
            "output_excerpt": self.output_excerpt,
            "status": self.status,
            "notes": self.notes,
        }


def excerpt(text: str, limit: int = 1200) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def markdown_cell(text: str) -> str:
    return text.replace("\n", " ").replace("|", "\\|")


def emit_live_log(agent_name: str, text: str) -> None:
    lines = text.splitlines(True) or [text]
    with PRINT_LOCK:
        for line in lines:
            suffix = "" if line.endswith("\n") else "\n"
            print(f"[{agent_name}] {line}", end=suffix, flush=True)


def signal_process_group(proc: subprocess.Popen[Any], sig: int) -> None:
    """Signal an agent process group, falling back to the main PID when needed."""
    try:
        os.killpg(proc.pid, sig)
        return
    except (ProcessLookupError, PermissionError):
        pass

    if proc.poll() is not None:
        return
    try:
        proc.send_signal(sig)
    except ProcessLookupError:
        pass


def classify_output(
    result: AgentResult,
    output: str,
    agent_cfg: dict[str, Any],
    defaults: dict[str, Any],
    user_task: str,
) -> None:
    body = log_body(output)
    body_cf = body.casefold()
    success_patterns = collect_patterns(agent_cfg, defaults, "success_patterns")
    failure_patterns = collect_patterns(agent_cfg, defaults, "failure_patterns")

    for pattern in success_patterns:
        if pattern_matches(body, pattern):
            result.success_pattern_hits.append(pattern)
    for pattern in failure_patterns:
        if pattern_matches(body, pattern):
            result.failure_pattern_hits.append(pattern)

    task_hints = extract_task_hints(user_task)
    for hint in task_hints:
        if hint in body or hint.casefold() in body_cf:
            result.task_hint_hits.append(hint)

    if result.exit_code not in (0, None):
        result.status = "failed"
        return
    if result.timed_out:
        result.status = "timeout"
        return
    if result.failure_pattern_hits:
        result.status = "failed"
        result.notes.append("Matched configured failure/derailment pattern.")
        return

    require_task_hints = bool(agent_setting(agent_cfg, defaults, "require_task_hints", False))
    min_body_chars = int(agent_setting(agent_cfg, defaults, "min_body_chars", 0) or 0)
    if min_body_chars and len(body) < min_body_chars:
        result.status = "failed"
        result.notes.append(f"Response body shorter than min_body_chars={min_body_chars}.")
        return

    has_success_signal = bool(result.success_pattern_hits)
    has_task_signal = enough_task_hint_hits(result.task_hint_hits, task_hints)

    if has_success_signal and (not require_task_hints or has_task_signal):
        result.status = "success"
        return
    if require_task_hints and has_task_signal and not result.failure_pattern_hits:
        result.status = "success"
        result.notes.append("Matched task hint keywords in response body.")
        return
    if result.exit_code == 0:
        result.status = "ambiguous"
        if require_task_hints and not has_task_signal:
            result.notes.append("Required task hint keywords missing from response body.")
        else:
            result.notes.append("Process exited 0 but no configured success pattern matched.")
        return
    result.status = "failed"


def verify_report_file(result: AgentResult) -> None:
    """Downgrade success when a report-output task did not write the expected file."""
    if not result.report_file:
        return
    if result.status not in {"success", "ambiguous"}:
        return
    path = Path(result.report_file)
    if path.is_file() and path.stat().st_size > 0:
        result.notes.append(f"Report file present: {result.report_file}")
        return
    result.status = "failed"
    result.notes.append(f"Expected report file missing or empty: {result.report_file}")


HEARTBEAT_SECONDS = 15


def _wrap_with_line_buffering(command: list[str]) -> tuple[list[str], bool]:
    """Wrap *command* with ``stdbuf -oL -eL`` when available.

    Agent CLIs commonly switch to fully-buffered stdout/stderr when their
    stdout is not a TTY, which delays the dispatcher's live log until the
    child has produced 4 KiB or finished. ``stdbuf`` forces line buffering
    so each newline reaches the dispatcher immediately, restoring the
    "continuous output" feel. When ``stdbuf`` is missing (rare non-POSIX),
    the original command is returned unchanged and the caller falls back
    to the previous behaviour.
    """
    if not command:
        return command, False
    if shutil.which("stdbuf"):
        return ["stdbuf", "-oL", "-eL", *command], True
    return list(command), False


def execute_agent_attempt(
    result: AgentResult,
    agent_cfg: dict[str, Any],
    model: str,
    workspace: str,
    user_task: str,
    task: str,
    timeout_seconds: int,
    log_path: Path,
    *,
    attempt_label: str = "primary",
) -> str:
    result.command = build_command(agent_cfg, model, workspace, user_task, task)
    started = time.monotonic()
    result.started = True
    output_parts: list[str] = []

    mode = "a" if attempt_label != "primary" and log_path.exists() else "w"
    line_buffered = False

    def record_output(logfh: Any, text: str) -> None:
        if not text:
            return
        output_parts.append(text)
        logfh.write(text)
        logfh.flush()
        emit_live_log(result.name, text)

    with log_path.open(mode, encoding="utf-8") as logfh:
        try:
            if attempt_label != "primary":
                logfh.write(f"\n\n# retry_attempt: {attempt_label}\n")
            else:
                logfh.write(f"# command: {format_command_for_log(result.command)}\n")
                logfh.write(f"# started: {datetime.now(timezone.utc).isoformat()}\n")
                logfh.write(f"# user_task: {user_task}\n")
                if result.content_footer:
                    logfh.write(f"# content_footer: {result.content_footer}\n")
                logfh.write("\n")
            if attempt_label != "primary":
                logfh.write(f"# command: {format_command_for_log(result.command)}\n\n")
            logfh.flush()

            wrapped_command, line_buffered = _wrap_with_line_buffering(result.command)
            proc = subprocess.Popen(
                wrapped_command,
                cwd=workspace,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                start_new_session=True,
            )

            assert proc.stdout is not None
            last_data_at = time.monotonic()
            last_heartbeat = last_data_at
            while True:
                if proc.poll() is not None:
                    remainder = proc.stdout.read()
                    record_output(logfh, remainder)
                    break

                ready, _, _ = select.select([proc.stdout], [], [], 0.2)
                if ready:
                    chunk = proc.stdout.readline()
                    if chunk:
                        record_output(logfh, chunk)
                        last_data_at = time.monotonic()
                        last_heartbeat = last_data_at

                now = time.monotonic()
                if now - last_data_at >= HEARTBEAT_SECONDS and now - last_heartbeat >= HEARTBEAT_SECONDS:
                    elapsed = int(now - started)
                    heartbeat = f"\n# ... still running ({elapsed}s, no output yet)\n"
                    logfh.write(heartbeat)
                    logfh.flush()
                    emit_live_log(result.name, heartbeat)
                    last_heartbeat = now

                if now - started >= timeout_seconds:
                    result.timed_out = True
                    result.exit_code = None
                    signal_process_group(proc, signal.SIGTERM)
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        signal_process_group(proc, signal.SIGKILL)
                        proc.wait()
                    remainder = proc.stdout.read()
                    record_output(logfh, remainder)
                    break

            if not result.timed_out:
                result.exit_code = proc.returncode
            else:
                timeout_line = f"\n\n# timed out after {timeout_seconds}s\n"
                logfh.write(timeout_line)
                logfh.flush()
                emit_live_log(result.name, timeout_line)
            if line_buffered:
                # Intentional: do not push stdbuf notes into result.notes (summary noise).
                logfh.write("# line_buffered: stdbuf -oL -eL\n")
                logfh.flush()
            if proc.stdout is not None:
                try:
                    proc.stdout.close()
                except Exception:
                    pass
        finally:
            result.duration_seconds += time.monotonic() - started
            result.finished = True

    attempt_output = "".join(output_parts)

    return attempt_output


def run_agent(
    name: str,
    agent_cfg: dict[str, Any],
    defaults: dict[str, Any],
    attribution_cfg: dict[str, Any],
    report_cfg: dict[str, Any],
    model: str,
    workspace: str,
    user_task: str,
    timeout_seconds: int,
    log_path: Path,
    *,
    force_attribution: bool = False,
    no_attribution: bool = False,
) -> AgentResult:
    result = AgentResult(name=name, enabled=True, model=model, command=[], log_path=str(log_path))
    if not agent_cfg.get("enabled", True):
        result.enabled = False
        result.status = "skipped"
        result.notes.append("disabled in config")
        return result

    binary = agent_cfg.get("binary", "")
    if not shutil.which(binary):
        result.status = "failed"
        result.notes.append(f"binary not found: {binary}")
        return result

    attributed_task, content_footer = apply_attribution(
        user_task,
        agent_cfg,
        attribution_cfg,
        force=force_attribution,
        disabled=no_attribution,
    )
    result.content_footer = content_footer
    reported_task, report_file = apply_report_output(attributed_task, report_cfg, name, workspace)
    if report_file:
        Path(report_file).parent.mkdir(parents=True, exist_ok=True)
        result.report_file = report_file
        result.notes.append(f"report_file: {report_file}")
    task = prepare_task(reported_task, defaults, agent_cfg)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    output = execute_agent_attempt(
        result,
        agent_cfg,
        model,
        workspace,
        user_task,
        task,
        timeout_seconds,
        log_path,
    )
    result.output_excerpt = excerpt(output)
    classify_output(result, output, agent_cfg, defaults, user_task)

    if should_retry_for_derailment(result, user_task, agent_cfg, defaults):
        retry_cfg = dict(agent_cfg)
        retry_cfg["_force_retry_args"] = True
        retry_cfg["_force_retry_prefix"] = True
        retry_task = prepare_task(reported_task, defaults, retry_cfg)
        result.failure_pattern_hits = []
        result.task_hint_hits = []
        result.success_pattern_hits = []
        result.timed_out = False
        result.notes.append("Retrying once without workspace bind after derailment.")
        output = execute_agent_attempt(
            result,
            retry_cfg,
            model,
            workspace,
            user_task,
            retry_task,
            timeout_seconds,
            log_path,
            attempt_label="derailment-retry",
        )
        result.output_excerpt = excerpt(output)
        classify_output(result, output, agent_cfg, defaults, user_task)
        if result.status == "success":
            result.notes.append("Recovered on derailment retry.")

    verify_report_file(result)
    return result


FOOTER_LINE_RE = re.compile(
    r"(?i)^(?:agent)\s*[：:]\s*([^,，\n]+?)\s*[,，]\s*(?:model)\s*[：:]\s*(.+?)\s*$"
)
CONFIG_MARKER_RE = re.compile(r"(?i)^agent[：:]([^,，]+),model[：:](.+)$")


def footer_signature(agent: str, model: str) -> str:
    return f"agent:{agent.strip().casefold()},model:{model.strip().casefold()}"


def parse_config_marker(marker: str) -> str | None:
    match = CONFIG_MARKER_RE.match(marker.strip())
    if not match:
        return None
    return footer_signature(match.group(1), match.group(2))


def extract_footer_from_body(body: str) -> tuple[str | None, str]:
    for line in reversed(body.splitlines()):
        line = line.strip()
        if not line:
            continue
        match = FOOTER_LINE_RE.match(line)
        if match:
            return footer_signature(match.group(1), match.group(2)), line
    return None, body.strip().splitlines()[-1] if body.strip() else ""


def run_cnb_json(cmd: list[str]) -> tuple[bool, Any]:
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return False, proc.stderr.strip() or proc.stdout.strip() or "cnb command failed"
    return True, json.loads(proc.stdout)


def fetch_cnb_pull_submissions(repo: str, pr_number: int, resource: str) -> tuple[bool, list[dict[str, Any]] | str]:
    ok, payload = run_cnb_json(
        [
            "cnb",
            "pulls",
            f"list-pull-{resource}",
            "--repo",
            repo,
            "--number",
            str(pr_number),
            "--page-size",
            "50",
            "--verbose",
        ]
    )
    if not ok:
        return False, str(payload)
    return True, payload.get("data", [])


def validate_cnb_reviews(
    repo: str,
    pr_number: int,
    required_markers: list[str],
    marker_agents: dict[str, str] | None = None,
    since_iso: str | None = None,
) -> dict[str, Any]:
    submissions: list[dict[str, Any]] = []
    for resource in ("reviews", "comments"):
        ok, data = fetch_cnb_pull_submissions(repo, pr_number, resource)
        if not ok:
            return {"ok": False, "error": data}
        for item in data:
            submissions.append(
                {
                    "id": item.get("id"),
                    "created_at": item.get("created_at", ""),
                    "body": item.get("body", ""),
                    "source": resource[:-1] if resource.endswith("s") else resource,
                }
            )

    marker_signatures: dict[str, str] = {}
    for marker in required_markers:
        signature = parse_config_marker(marker)
        if signature:
            marker_signatures[signature] = marker

    matched: list[dict[str, Any]] = []
    matched_signatures: set[str] = set()
    for submission in submissions:
        body = submission.get("body", "")
        created = submission.get("created_at", "")
        if since_iso and created and created < since_iso:
            continue

        exact_marker = next((marker for marker in required_markers if marker in body), None)
        signature, tail = extract_footer_from_body(body)
        normalized_marker = marker_signatures.get(signature or "", "")
        marker = exact_marker or normalized_marker
        if not marker or (signature and signature in matched_signatures):
            continue

        match_mode = "exact" if exact_marker else "normalized"
        if signature:
            matched_signatures.add(signature)
        matched.append(
            {
                "id": submission.get("id"),
                "created_at": created,
                "marker": marker,
                "agent": (marker_agents or {}).get(marker, ""),
                "match_mode": match_mode,
                "source": submission.get("source", "review"),
                "tail": tail,
            }
        )

    unmatched_markers = [
        marker
        for marker in required_markers
        if parse_config_marker(marker) not in matched_signatures and marker not in {row["marker"] for row in matched}
    ]
    return {
        "ok": True,
        "repo": repo,
        "pr_number": pr_number,
        "matched": matched,
        "unmatched_markers": unmatched_markers,
        "required_markers": required_markers,
    }


def render_markdown_summary(run_dir: Path, results: list[AgentResult], cnb_report: dict[str, Any] | None) -> str:
    lines = [
        "# Multi-Agent CLI Dispatch Report",
        "",
        f"- Run directory: `{run_dir}`",
        f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Agent Results",
        "",
        "| Agent | Model | Status | Exit | Duration(s) | Signals | Notes | Log |",
        "|---|---|---:|---:|---:|---|---|---|",
    ]
    for item in results:
        signals = []
        if item.success_pattern_hits:
            signals.append("success:" + ",".join(item.success_pattern_hits[:3]))
        if item.task_hint_hits:
            signals.append("hints:" + ",".join(item.task_hint_hits[:3]))
        if item.failure_pattern_hits:
            signals.append("fail:" + ",".join(item.failure_pattern_hits[:2]))
        signal_text = "; ".join(signals) or "-"
        notes_text = "; ".join(item.notes[:2]) or "-"
        log_name = Path(item.log_path).name if item.log_path else "-"
        exit_code = "-" if item.exit_code is None else str(item.exit_code)
        model_text = item.model or "-"
        lines.append(
            f"| {item.name} | {markdown_cell(model_text)} | {item.status} | {exit_code} | "
            f"{item.duration_seconds:.1f} | {markdown_cell(signal_text)} | "
            f"{markdown_cell(notes_text)} | `{log_name}` |"
        )

    footers = [item for item in results if item.content_footer]
    if footers:
        lines.extend(["", "## Attribution Footers", ""])
        for item in footers:
            lines.append(f"- `{item.name}`: `{item.content_footer}`")

    if cnb_report is not None:
        lines.extend(["", "## CNB Validation", ""])
        if not cnb_report.get("ok"):
            lines.append(f"- Failed: {cnb_report.get('error', 'unknown error')}")
        else:
            matched = cnb_report.get("matched", [])
            if matched:
                for row in matched:
                    agent_label = row.get("agent") or "unknown"
                    source = row.get("source", "review")
                    mode = row.get("match_mode", "exact")
                    mode_note = " (normalized footer match)" if mode == "normalized" else ""
                    lines.append(
                        f"- Matched `{agent_label}` {source} `{row['id']}` "
                        f"({row['created_at']}) footer `{row['marker']}`{mode_note}"
                    )
            else:
                lines.append("- No matching CNB review/comment markers found for this run.")
            unmatched = cnb_report.get("unmatched_markers", [])
            if unmatched:
                lines.append("- Unmatched configured footers:")
                for marker in unmatched:
                    lines.append(f"  - `{marker}`")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Dispatch a task to multiple coding-agent CLIs.")
    parser.add_argument("--task", required=True, help="Task content passed to each CLI.")
    parser.add_argument(
        "--workspace",
        default=os.getcwd(),
        help="Working directory for CLI execution.",
    )
    parser.add_argument(
        "--skill-dir",
        default=str(Path(__file__).resolve().parents[1]),
        help="Skill directory containing agents.default.toml / agents.toml.",
    )
    parser.add_argument(
        "--agents",
        default="",
        help="Comma-separated agent names to run; default = all enabled agents.",
    )
    parser.add_argument(
        "--model-overrides",
        default="",
        help='JSON object of per-agent model overrides, e.g. {"claude":"claude-opus-4-8[1m]"}',
    )
    parser.add_argument(
        "--validate-cnb",
        action="store_true",
        help="Run optional CNB review validation after dispatch.",
    )
    parser.add_argument("--cnb-repo", default="")
    parser.add_argument("--cnb-pr", type=int, default=0)
    parser.add_argument(
        "--cnb-markers",
        default="",
        help="Comma-separated agent markers required in new CNB review bodies.",
    )
    parser.add_argument(
        "--no-task-prefix",
        action="store_true",
        help="Disable the anti-derailment task prefix for this run.",
    )
    parser.add_argument(
        "--force-attribution",
        action="store_true",
        help="Append per-agent CNB/GitHub content footer instructions even if auto-detect does not match.",
    )
    parser.add_argument(
        "--no-attribution",
        action="store_true",
        help="Disable per-agent content footer instructions for this run.",
    )
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    workspace = str(Path(args.workspace).resolve())
    config = load_config(skill_dir)

    run_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path(config.get("defaults", {}).get("log_dir") or (skill_dir / "runs" / run_stamp))
    run_dir.mkdir(parents=True, exist_ok=True)

    selected = [name.strip() for name in args.agents.split(",") if name.strip()]
    model_overrides = json.loads(args.model_overrides) if args.model_overrides else {}

    agents_section = config.get("agents", {})
    agent_names = selected or list(agents_section.keys())

    defaults = dict(config.get("defaults", {}))
    attribution_cfg = dict(config.get("attribution", {}))
    report_cfg = dict(config.get("report_output", {}))
    if args.no_task_prefix:
        defaults["apply_task_prefix"] = False
    default_timeout = int(defaults.get("timeout_seconds", 600))
    dispatch_started = datetime.now(timezone.utc).isoformat()

    futures = {}
    results: list[AgentResult] = []
    with ThreadPoolExecutor(max_workers=len(agent_names) or 1) as pool:
        for name in agent_names:
            agent_cfg = agents_section.get(name)
            if not agent_cfg:
                results.append(
                    AgentResult(
                        name=name,
                        enabled=False,
                        status="skipped",
                        notes=[f"unknown agent: {name}"],
                    )
                )
                continue
            model = model_overrides.get(name, agent_cfg.get("model", ""))
            timeout_seconds = int(agent_cfg.get("timeout_seconds", default_timeout))
            log_path = run_dir / f"{name}.log"
            futures[
                pool.submit(
                    run_agent,
                    name,
                    agent_cfg,
                    defaults,
                    attribution_cfg,
                    report_cfg,
                    model,
                    workspace,
                    args.task,
                    timeout_seconds,
                    log_path,
                    force_attribution=args.force_attribution,
                    no_attribution=args.no_attribution,
                )
            ] = name

        for future in as_completed(futures):
            agent_name = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                results.append(
                    AgentResult(
                        name=agent_name,
                        enabled=True,
                        status="failed",
                        log_path=str(run_dir / f"{agent_name}.log"),
                        notes=[f"agent thread raised: {type(exc).__name__}: {exc}"],
                    )
                )

    results.sort(key=lambda item: item.name)
    cnb_report = None
    if args.validate_cnb or config.get("cnb_validation", {}).get("enabled"):
        repo = args.cnb_repo or config.get("cnb_validation", {}).get("repo", "")
        pr_number = args.cnb_pr or int(config.get("cnb_validation", {}).get("pr_number", 0) or 0)
        markers_raw = args.cnb_markers or ",".join(config.get("cnb_validation", {}).get("required_agent_markers", []))
        markers = [m.strip() for m in markers_raw.split(",") if m.strip()]
        if not markers:
            selected_names = selected or list(agents_section.keys())
            markers = [
                str(agents_section[name].get("content_footer", "")).strip()
                for name in selected_names
                if agents_section.get(name, {}).get("content_footer")
            ]
        if repo and pr_number and markers:
            selected_names = selected or list(agents_section.keys())
            marker_agents = {
                str(agents_section[name].get("content_footer", "")).strip(): name
                for name in selected_names
                if agents_section.get(name, {}).get("content_footer")
            }
            cnb_report = validate_cnb_reviews(
                repo,
                pr_number,
                markers,
                marker_agents=marker_agents,
                since_iso=dispatch_started,
            )

    summary = {
        "run_dir": str(run_dir),
        "workspace": workspace,
        "task_excerpt": excerpt(args.task, 300),
        "started_at": dispatch_started,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "results": [item.to_dict() for item in results],
        "cnb_validation": cnb_report,
    }

    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (run_dir / "summary.md").write_text(render_markdown_summary(run_dir, results, cnb_report), encoding="utf-8")

    print((run_dir / "summary.md").read_text(encoding="utf-8"))
    failed = [item for item in results if item.status in {"failed", "timeout"}]
    ambiguous = [item for item in results if item.status == "ambiguous"]
    return 1 if failed else (2 if ambiguous else 0)


if __name__ == "__main__":
    sys.exit(main())
