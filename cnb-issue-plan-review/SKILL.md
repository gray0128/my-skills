---
name: cnb-issue-plan-review
description: Review a CNB Issue implementation plan before coding. Use when Codex is asked to review, audit, validate, check, or comment on an Issue plan; to assess whether a proposed CNB Issue plan has clear scope, out-of-scope, acceptance criteria, implementation approach, documentation/contract impact, verification, risks, and dependencies; or to post an advisory plan-review Issue comment without implementing code.
---

# CNB Issue Plan Review

Use this skill to review an Issue plan. The result is advisory by default unless the user or repository instructions explicitly make plan review a gate. Do not implement code, open PRs, merge, or expand scope from this skill.

## Workflow

1. Resolve the repository and Issue number.
2. Read the Issue body, all comments, activities, and the latest applicable implementation plan comment.
3. Read relevant repository instructions, docs, API specs, contracts, tests, and code needed to judge the plan.
4. Check for duplicate active Issues, branches, or PRs when ownership may affect the plan.
5. Review the plan for feasibility, scope control, acceptance criteria, documentation/contract impact, verification adequacy, risks, and dependencies.
6. Post an Issue comment using `assets/issue-plan-review-comment.md`.

Read `references/cnb-issue-plan-review-commands.md` before constructing CNB commands.

## Review Criteria

- `Scope` is concrete and executable.
- `Out of Scope` prevents foreseeable expansion.
- `Acceptance Criteria` are observable pass/fail checks.
- `Implementation Approach` is compatible with repository architecture and conventions.
- `Documentation And Contracts` lists affected docs/contracts or clearly explains why none are needed.
- `Verification` includes tests, manual checks, and doc/contract checks when applicable.
- Risks, migrations, compatibility concerns, and dependencies are explicit.
- Latest human decisions in comments are reflected.

## Result

Use one advisory result:

- `ready_for_execution`: plan is clear enough to implement.
- `revise_before_execution`: plan needs changes before implementation.
- `needs_human_decision`: a human decision is required before implementation.

For every CNB Issue comment you submit, append the current agent/model marker as the last non-empty line. Use actual current values in the format `Agent：<current-agent>，Model：<current-model>`; for example, `Agent：codex，Model：GPT-5.5`.
