---
name: cnb-workflow-continue
description: Inspect CNB Issue or PR workflow state and choose the next safe step. Use when Codex is asked to continue, resume, inspect status, determine next action, audit workflow progress, or route work for a CNB Issue/PR. Reads live Issue, PR, comments, reviews, checks, branches, and closeout evidence; reports the current state; and recommends the next CNB workflow skill such as issue handling, plan review, PR review, review feedback handling, CI repair, or PR merge.
---

# CNB Workflow Continue

Use this skill to inspect state and route the next action. By default, it does not modify code, post comments, push, review, or merge. If the user explicitly asks to continue after the state report, invoke the appropriate next workflow skill.

## Workflow

1. Resolve whether the target is an Issue, PR, branch, or repository-wide task.
2. Read live CNB state: Issue body/comments/activities, PR metadata/comments/reviews/commits/files/checks, linked Issues, and branch existence as applicable.
3. Compare the observed state with `assets/workflow-state-report.md`.
4. Identify blockers, stale evidence, missing plan, failing checks, requested changes, merge readiness, or closeout gaps.
5. Recommend exactly one next primary skill and any secondary checks.

Read `references/cnb-workflow-continue-commands.md` before constructing CNB or git commands.

## Routing Rules

- No Issue exists and the user wants one: `cnb-issue-create`.
- Issue exists but no executable plan is present: `cnb-issue-handle` plan stage.
- Issue plan needs advisory review: `cnb-issue-plan-review`.
- Issue has executable plan but no PR: `cnb-issue-handle` execution stage.
- PR has failing checks: `cnb-pr-fix-ci`.
- PR has requested changes or unresolved blocking review feedback: `cnb-pr-address-review`.
- PR needs independent review: `cnb-pr-review`.
- PR is approved/review-clean, checks pass, and user explicitly authorized merge: `cnb-pr-merge`.
- PR is merged but closeout evidence is incomplete: `cnb-pr-merge` closeout verification.
- State is ambiguous or conflicting: stop and ask for a human decision.

## Rules

- Prefer latest explicit human decision over stale Issue/PR text.
- Treat review evidence as valid only for the current PR head SHA.
- Do not skip directly from open PR to merge without review/readiness evidence and active human merge authorization.
- Do not report completion while required CI, Issue closeout, branch cleanup, or main CI is unknown.

If this skill posts a CNB status comment by explicit request, append the current agent/model marker as the last non-empty line. Use actual current values in the format `Agent：<current-agent>，Model：<current-model>`; for example, `Agent：codex，Model：GPT-5.5`.
