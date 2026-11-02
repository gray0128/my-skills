#!/usr/bin/env python3
"""Validate the review-conclusion analysis report structure."""

from __future__ import annotations

import sys
from pathlib import Path


REQUIRED_HEADINGS = [
    "# 评审报告分析采纳结论",
    "## 结论摘要",
    "## 依据来源",
    "## 逐项分析",
    "## 采纳与处理计划",
    "## 风险与待确认事项",
]

DECISION_LABELS = [
    "采纳-立即处理",
    "采纳-纳入后续计划",
    "部分采纳",
    "不采纳",
    "已解决",
    "需人工决策",
]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_report.py <path/to/评审报告分析采纳结论.md>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    errors: list[str] = []

    if path.name != "评审报告分析采纳结论.md":
        errors.append("report filename must be exactly 评审报告分析采纳结论.md")

    if not path.is_file():
        errors.append(f"report file does not exist: {path}")
    else:
        text = path.read_text(encoding="utf-8")
        for heading in REQUIRED_HEADINGS:
            if heading not in text:
                errors.append(f"missing required heading: {heading}")
        if "<" in text and ">" in text:
            errors.append("report still appears to contain angle-bracket placeholders")
        if "TODO" in text.upper():
            errors.append("report still contains TODO text")
        if not any(label in text for label in DECISION_LABELS):
            errors.append("report does not contain any recognized decision labels")

    if errors:
        for error in errors:
            print(f"[FAIL] {error}", file=sys.stderr)
        return 1

    print(f"[OK] {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
