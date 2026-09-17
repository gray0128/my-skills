---
name: cnb-pr-fix-ci
description: Diagnose and fix failing CNB PR checks or build pipelines. Use when Codex is asked to investigate failed CI, fix red checks, inspect CNB build logs, repair .cnb.yml or test/lint/build failures, or push a minimal PR update after CI failure. Reads live PR checks and build logs, identifies the smallest fix, updates code/docs/contracts or pipeline config as needed, runs focused verification, pushes to the existing PR branch, and posts a CI fix summary.
---

# CNB PR Fix CI

Use this skill to repair failing CI on an existing CNB PR. Do not perform general feature work, independent PR review, merge, or close Issues from this skill.

## Workflow

1. Resolve the repository and PR number.
2. Read live PR metadata, source branch, current head SHA, commit statuses, and failing build logs.
3. Classify the failure: test, lint, build, dependency, environment, pipeline configuration, flaky/external, permission, or unknown.
4. If `.cnb.yml` or pipeline behavior is involved, use the existing `cnb-pipeline` workflow and validator before editing.
5. Switch to the PR source branch and pull latest state.
6. Apply the smallest fix that addresses the failing check. Include docs/contracts only when the fix changes public behavior, interfaces, configuration, pipeline behavior, or skill instructions.
7. Run the most focused local verification available.
8. Commit, push, and post `assets/ci-fix-summary.md` to the PR.

Read `references/cnb-pr-fix-ci-commands.md` before constructing CNB, build, or git commands.

## Rules

- Do not guess from check names alone; inspect logs whenever available.
- Do not refactor unrelated code while fixing CI.
- Do not repeatedly poll CI after pushing. Push the fix, post the evidence, and let the platform run checks unless the user explicitly asks to wait.
- If logs show external outage, permission problems, or missing secrets, do not fake a code fix; report the operational blocker.

## Stop Conditions

Stop and report the blocker when:

- The failing check or build log cannot be read.
- The failure cause is unrelated to the PR and requires infrastructure or secret changes.
- The source branch cannot be checked out safely.
- A local reproduction command fails for a different reason after the intended fix.
- Push fails.

For every CNB PR comment you submit, append the current agent/model marker as the last non-empty line. Use actual current values in the format `Agent：<current-agent>，Model：<current-model>`; for example, `Agent：codex，Model：GPT-5.5`.
