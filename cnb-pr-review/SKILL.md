---
name: cnb-pr-review
description: Review CNB pull requests with Issue traceability, exact head-SHA binding, code/security/regression analysis, verification evidence, and formal CNB Pull Review submission. Use when Codex is asked to review, audit, inspect, approve, request changes on, or comment on a CNB PR; to compare a PR against linked Issues, implementation plans, comments, activities, CI checks, and diff; or to submit structured review findings and line-level comments through CNB.
---

# CNB PR Review

Use this skill to independently review one CNB PR. Do not implement fixes, push code, merge the PR, close Issues, or expand the requested scope from this skill.

## Core Workflow

1. Resolve the target repository and PR number.
2. Read live PR, Issue, review, CI, and diff context.
3. Determine whether the current CNB review user is the PR author.
4. Perform spec, code, and verification review against the current PR head SHA.
5. Submit a CNB review or comment using the bundled template and the author/self-review gate.
6. Return the review result and evidence summary.

Read `references/cnb-pr-review-commands.md` before constructing CNB or git commands.

## Context Collection

Collect enough information to review the PR without relying on stale summaries:

- PR metadata, title, body, source branch, base branch, current head SHA, author, state, and WIP status.
- Current CNB review user from environment, event context, or `cnb users get-user-info --verbose`.
- PR comments, formal reviews, commits, changed files, and current check status.
- Linked Issues from `Closes`, `Fixes`, `Resolves`, `Ref`, or explicit user context.
- Linked Issue body, comments, and activities, including any implementation plan comment.
- Repository instructions such as `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, or project workflow skills.
- Relevant local docs, API specs, tests, and changed source files.
- Exact diff for the current base/head pair.

If the PR changes a skill, read the changed skill's `SKILL.md` completely and inspect directly relevant bundled resources. If the PR changes `.cnb.yml` or pipeline behavior, use the existing `cnb-pipeline` workflow for syntax and behavioral checks.

## Author Gate

Before deciding the submission event, compare the PR author with the current CNB review user:

- If they differ, submit the review normally according to the review result.
- If they match, do not submit `approve` or `request_changes`. CNB may reject self-review, and even when it accepts a comment, it should not be treated as formal approval.
- If they match and repository instructions explicitly define a single-maintainer exception, submit the review as `--event comment`, set `Review Submission: single_maintainer_comment`, and set `Single Maintainer Exception: true`.
- If they match and no explicit single-maintainer exception applies, submit the review result as a comment-only review with `--event comment` or, if needed, `post-pull-comment`. Set `Review Submission: author_self_comment` and `Single Maintainer Exception: false`.
- If the current CNB review user cannot be determined reliably, do not approve. Submit `blocked` or a comment-only review explaining that reviewer identity could not be verified.

This gate affects submission mechanics only. Still complete the spec, code, and verification review and report findings clearly.

## Review Passes

Run all three passes against the same current head SHA:

1. **Spec review**: compare implementation to linked Issues, submitted plans, later human decisions, scope, out-of-scope, and acceptance criteria.
2. **Code review**: inspect changed code for correctness, security, regressions, maintainability, edge cases, and test coverage.
3. **Verification review**: run or independently confirm declared verification commands and current CI status when available.

Focus findings on behavior that can block correctness or maintainability. Ignore pure style issues that project tooling should handle unless they hide a real bug.

## Review Result

Use `assets/pr-review-comment.md` for the review body. Set exactly one result:

- `approved`: no blocking issues, current CI/declared checks are successful or justifiably not required, the reviewer agent differs from the implementer agent, and author gate permits approval. When author gate blocks formal approval, the result may still say the code is review-clean, but submission must be comment-only.
- `changes_requested`: actionable blocking issues exist and the PR author should change code or tests. When author gate blocks formal request-changes, submit the same findings as comment-only.
- `blocked`: review cannot be completed because required context, checks, permissions, or head-SHA consistency cannot be verified.

The review body must record:

- Current `Reviewed Head SHA`.
- PR author, current review user, and whether they match.
- Implementer and reviewer agent identities when known.
- Linked Issue and execution plan evidence.
- Plan compliance or `not_applicable`.
- Findings with file and line references when applicable.
- Verification commands and outcomes.
- Risks or follow-ups.

Approval is valid only for the recorded head SHA. If the PR changes after review, a new review is required.

## Submission Rules

Submit the result as a formal CNB Pull Review:

- `approved` -> `--event approve`
- `changes_requested` -> `--event request_changes`
- `blocked` -> `--event comment`

Apply the author gate before submitting. If the PR author and current review user are the same and no explicit single-maintainer exception applies, override `approve` or `request_changes` to `--event comment` and record `Review Submission: author_self_comment`.

Prefer line-level review comments for actionable code findings. Keep at most 10 line comments, prioritizing correctness, security, and regression risks.

If CNB rejects formal approval because the only available CNB account authored the PR, do not silently convert it to approval. Record the rejection and submit the same body as a commented review only when repository instructions explicitly allow a single-maintainer exception; otherwise submit a normal comment-only review.

For every CNB comment, review body, or line-level review comment you submit, append the current agent/model marker as the last non-empty line. Use actual current values in the format `Agent：<current-agent>，Model：<current-model>`; for example, `Agent：codex，Model：GPT-5.5`.

## Stop Conditions

Stop and report `blocked` when:

- The target repo or PR number is ambiguous.
- PR metadata, current head SHA, diff, or linked Issue context cannot be read.
- The current head SHA changes during review.
- Required verification cannot be run or confirmed.
- The current CNB review user cannot be distinguished from the PR author and the user specifically requested formal approval.
- CNB review submission fails after a safe retry.

Never merge from this workflow.
