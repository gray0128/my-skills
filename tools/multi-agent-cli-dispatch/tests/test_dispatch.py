#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import signal
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock


SKILL_DIR = Path(__file__).resolve().parents[1]
DISPATCH_PATH = SKILL_DIR / "scripts" / "dispatch.py"


def load_dispatch_module():
    spec = importlib.util.spec_from_file_location("multi_agent_dispatch", DISPATCH_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class DispatchClassificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dispatch = load_dispatch_module()
        cls.config = cls.dispatch.load_config(SKILL_DIR)
        cls.defaults = cls.config["defaults"]
        cls.agy_cfg = cls.config["agents"]["agy"]

    def classify_agy(self, output: str, task: str):
        result = self.dispatch.AgentResult(name="agy", enabled=True, exit_code=0)
        self.dispatch.classify_output(result, output, self.agy_cfg, self.defaults, task)
        return result

    def test_agy_add_dir_derailment_fails_and_skips_retry_for_skill_task(self) -> None:
        task = '使用 skill "cnb-pr-review" 审核 PR https://cnb.cool/ifilfy/user-workbench/-/pulls/145'
        output = """
在 **Antigravity CLI (`agy`)** 中，`--add-dir` 是一个命令行参数，用于在启动会话时向当前工作空间添加目录。

项目中的配置与引用：
- agents.default.toml
- cli-invocation.md
"""

        result = self.classify_agy(output, task)

        self.assertEqual(result.status, "failed")
        self.assertTrue(result.failure_pattern_hits)
        self.assertFalse(self.dispatch.should_retry_for_derailment(result, task, self.agy_cfg, self.defaults))
        self.assertIn("Skipping derailment retry", "; ".join(result.notes))

    def test_agy_skill_pr_review_task_does_not_bind_workspace(self) -> None:
        task = '使用 skill "cnb-pr-review" 审核 PR https://cnb.cool/ifilfy/user-workbench/-/pulls/145'

        args = self.dispatch.resolve_args_before_task(self.agy_cfg, "/tmp/workspace", task)

        self.assertIn("--print", args)
        self.assertNotIn("--add-dir", args)
        self.assertNotIn("/tmp/workspace", args)

    def test_agy_code_task_still_binds_workspace(self) -> None:
        task = "修复 TypeScript 测试失败"

        args = self.dispatch.resolve_args_before_task(self.agy_cfg, "/tmp/workspace", task)

        self.assertIn("--print", args)
        self.assertIn("--add-dir", args)
        self.assertIn("/tmp/workspace", args)

    def test_agy_refusal_does_not_pass_from_task_hints(self) -> None:
        task = '使用 skill "cnb-pr-review" 审核 PR https://cnb.cool/ifilfy/user-workbench/-/pulls/145'
        output = """
由于您要求不使用任何工具，我无法访问或获取该 PR 的内容。同时，我的可用 skill 列表中并没有 `cnb-pr-review`。

因此，我无法对该 PR 进行审核，也无法给出具体的评审结论。
"""

        result = self.classify_agy(output, task)

        self.assertEqual(result.status, "failed")
        self.assertIn("无法访问或获取该 PR", result.failure_pattern_hits)
        self.assertTrue(result.task_hint_hits)

    def test_footer_normalization_matches_cnb_review_footer(self) -> None:
        expected = self.dispatch.parse_config_marker("agent：reasonix,model:deepseek-v4-pro")
        actual, tail = self.dispatch.extract_footer_from_body(
            "审核完成。\n\nAgent：reasonix，Model：deepseek-v4-pro"
        )

        self.assertEqual(actual, expected)
        self.assertEqual(tail, "Agent：reasonix，Model：deepseek-v4-pro")

    def test_summary_includes_notes_and_model(self) -> None:
        result = self.dispatch.AgentResult(
            name="agy",
            enabled=True,
            model="Gemini 3.5 Flash (High)",
            exit_code=0,
            duration_seconds=1.2,
            log_path=str(SKILL_DIR / "runs" / "test" / "agy.log"),
            status="failed",
            notes=["Matched configured failure/derailment pattern."],
        )

        summary = self.dispatch.render_markdown_summary(SKILL_DIR / "runs" / "test", [result], None)

        self.assertIn(
            "| Agent | Model | Status | Exit | Duration(s) | Signals | Notes | Log |",
            summary,
        )
        self.assertIn("Gemini 3.5 Flash (High)", summary)
        self.assertIn("Matched configured failure/derailment pattern.", summary)

    def test_default_timeouts_are_ten_minutes(self) -> None:
        self.assertEqual(self.defaults["timeout_seconds"], 600)
        for agent_cfg in self.config["agents"].values():
            self.assertEqual(agent_cfg["timeout_seconds"], 600)

    def test_code_quality_task_gets_per_agent_report_output_instruction(self) -> None:
        task, report_file = self.dispatch.apply_report_output(
            "请做一次代码质量检查并输出报告",
            self.config["report_output"],
            "grok",
            "/tmp/workspace",
        )

        self.assertEqual(report_file, "/tmp/workspace/docs/评审/grok/report.md")
        self.assertIn("/tmp/workspace/docs/评审/grok/report.md", task)
        self.assertIn("本任务需要产出代码质量检查报告", task)

    def test_pr_review_task_does_not_get_report_output_instruction(self) -> None:
        user_task = '使用 skill "cnb-pr-review" 审核 PR https://cnb.cool/ifilfy/user-workbench/-/pulls/145'
        task, report_file = self.dispatch.apply_report_output(
            user_task,
            self.config["report_output"],
            "grok",
            "/tmp/workspace",
        )

        self.assertEqual(task, user_task)
        self.assertIsNone(report_file)

    def test_extract_task_hints_drops_url_noise(self) -> None:
        task = '使用 skill "cnb-pr-review" 审核 PR https://cnb.cool/ifilfy/user-workbench/-/pulls/145'
        hints = self.dispatch.extract_task_hints(task)

        self.assertIn("cnb-pr-review", hints)
        self.assertIn("145", hints)
        self.assertIn("审核", hints)
        self.assertNotIn("https", hints)
        self.assertNotIn("cool", hints)
        self.assertNotIn("pulls", hints)
        self.assertNotIn("skill", hints)

    def test_url_echo_alone_is_not_enough_task_signal(self) -> None:
        task = '使用 skill "cnb-pr-review" 审核 PR https://cnb.cool/ifilfy/user-workbench/-/pulls/145'
        # Body only restates host crumbs and one weak token — should not pass.
        output = "# user_task: x\n\nhttps://cnb.cool/ example"
        result = self.dispatch.AgentResult(name="grok", enabled=True, exit_code=0)
        self.dispatch.classify_output(result, output, self.config["agents"]["grok"], self.defaults, task)
        self.assertEqual(result.status, "ambiguous")

    def test_missing_report_file_fails_success(self) -> None:
        result = self.dispatch.AgentResult(
            name="grok",
            enabled=True,
            exit_code=0,
            status="success",
            report_file="/tmp/does-not-exist-multi-agent-dispatch-report.md",
        )
        self.dispatch.verify_report_file(result)
        self.assertEqual(result.status, "failed")
        self.assertTrue(any("missing or empty" in note for note in result.notes))

    def test_default_task_prefix_allows_autonomous_skills(self) -> None:
        prefix = self.defaults["task_prefix"]
        self.assertNotIn("否则不要自行引入其他 workflow 或 skill", prefix)
        self.assertIn("如果任务要求使用某个 skill，按任务说明执行", prefix)

    def test_general_failure_patterns_do_not_use_bare_error(self) -> None:
        patterns = self.defaults["general_failure_patterns"]
        self.assertNotIn("error:", patterns)
        self.assertNotIn("Error:", patterns)
        self.assertNotIn("错误：", patterns)
        self.assertIn("RESOURCE_EXHAUSTED", patterns)

    def test_grok_build_command_includes_effort_high(self) -> None:
        grok = self.config["agents"]["grok"]
        cmd = self.dispatch.build_command(
            grok,
            grok["model"],
            "/tmp/workspace",
            "hello",
            "hello",
        )
        self.assertEqual(cmd[0], "grok")
        self.assertIn("-m", cmd)
        self.assertIn("grok-4.5", cmd)
        self.assertIn("--effort", cmd)
        self.assertIn("high", cmd)

    def test_signal_process_group_falls_back_on_permission_error(self) -> None:
        proc = subprocess.Popen(["sleep", "30"], start_new_session=True)
        try:
            with mock.patch.object(self.dispatch.os, "killpg", side_effect=PermissionError(1, "Operation not permitted")):
                self.dispatch.signal_process_group(proc, signal.SIGTERM)
            proc.wait(timeout=5)
            self.assertIsNotNone(proc.returncode)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()

    def test_wrap_with_line_buffering_uses_stdbuf_when_available(self) -> None:
        with mock.patch.object(self.dispatch.shutil, "which", return_value="/usr/bin/stdbuf"):
            wrapped, applied = self.dispatch._wrap_with_line_buffering(["claude", "-p", "hi"])
        self.assertTrue(applied)
        self.assertEqual(wrapped, ["stdbuf", "-oL", "-eL", "claude", "-p", "hi"])

    def test_wrap_with_line_buffering_falls_back_when_stdbuf_missing(self) -> None:
        with mock.patch.object(self.dispatch.shutil, "which", return_value=None):
            wrapped, applied = self.dispatch._wrap_with_line_buffering(["claude", "-p", "hi"])
        self.assertFalse(applied)
        self.assertEqual(wrapped, ["claude", "-p", "hi"])

    def test_execute_agent_attempt_emits_heartbeat_for_silent_child(self) -> None:
        # Use a fake binary that ignores its argv and just sleeps, so neither the
        # model flag nor args_before_task can short-circuit the test. This lets
        # the heartbeat fire before the timeout hits.
        fake_bin = Path(self._tmpd()) / "fake_agent.sh"
        fake_bin.write_text("#!/bin/sh\nsleep 30\n", encoding="utf-8")
        fake_bin.chmod(0o755)

        agent_cfg = {
            "binary": str(fake_bin),
            "args_before_task": [],
            "model_flag": "--model",
            "model_flag_style": "space",
        }
        import tempfile

        with tempfile.TemporaryDirectory() as tmpd:
            log_path = Path(tmpd) / "silent.log"
            result = self.dispatch.AgentResult(
                name="silent-agent", enabled=True, log_path=str(log_path)
            )
            with mock.patch.object(self.dispatch, "HEARTBEAT_SECONDS", 1):
                self.dispatch.execute_agent_attempt(
                    result,
                    agent_cfg,
                    "test-model",
                    str(Path.cwd()),
                    "ignored",
                    "ignored",
                    timeout_seconds=3,
                    log_path=log_path,
                )
            with log_path.open(encoding="utf-8") as fh:
                body = fh.read()
        self.assertIn("still running", body)
        self.assertTrue(result.timed_out)

    def _tmpd(self) -> str:
        import tempfile
        return tempfile.mkdtemp()


if __name__ == "__main__":
    unittest.main()
