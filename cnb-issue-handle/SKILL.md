---
name: cnb-issue-handle
description: Handle an existing CNB Issue from intake through implementation and PR creation. Use when Codex is asked to process, handle, fix, implement, execute, continue, or resolve a CNB Issue; to read Issue context and related skill/project information; to post an implementation plan as an Issue comment before coding; to update code plus required docs, contracts, API specs, behavior notes, or pipeline documentation; to create a branch, make focused changes, run verification, push, and open a PR using a required PR description template linked to the Issue.
---

# CNB Issue Handle

Use this skill to process one existing CNB Issue through PR creation. Do not use it to create new Issues, perform independent PR review, merge PRs, or close Issues after merge.

## Mandatory Stages

1. Intake and context collection.
2. Plan comment on the Issue.
3. Execution and verification.
4. PR creation with the bundled template.

Do not start coding before the Issue plan comment is submitted, except for read-only exploration needed to understand the repository.

## Stage 1: Intake And Context

Read `references/cnb-issue-handle-commands.md` before constructing CNB commands.

Collect enough information to make the implementation plan executable:

- Resolve the repository and Issue number from the user, `CNB_REPO_SLUG`, and `CNB_ISSUE_IID`.
- Read the Issue body, all comments, and activities with verbose output.
- Check for existing open PRs or active branches that already handle the Issue.
- Read repository instructions such as `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, or project-specific workflow skills.
- Read relevant local docs, API specs, tests, and code before planning.
- If the Issue concerns a skill, read the target skill's `SKILL.md` completely, list its bundled resources, and read directly relevant `references/`, `assets/`, or `scripts/` files before planning.
- If the Issue references TAPD, use the existing `cnb-tapd-resource-fetcher` workflow.
- If the Issue depends on live repository knowledge, use the existing `cnb-repo-knowledge-base` workflow.
- If the Issue changes `.cnb.yml` or pipeline behavior, use the existing `cnb-pipeline` workflow before editing.
- Identify any documentation or contract surfaces affected by the requested change, including README files, user guides, API specs, schemas, CLI help, configuration docs, pipeline docs, skill instructions, generated docs, and architecture or compatibility contracts.

Stop and ask or comment on the Issue when the latest human decision, scope, or acceptance criteria conflict.

## Stage 2: Plan Comment

Draft the plan with `assets/issue-plan-comment.md`, then submit it as an Issue comment before coding.

The plan must include:

- Scope and out of scope.
- Acceptance criteria.
- Implementation approach.
- Files or modules expected to change.
- Documentation and contract impact: list files to update, or explicitly state `None` with the reason.
- Verification commands or manual checks.
- Risks, dependencies, and open questions.

If the request is plan-only, stop after submitting the plan. If scope is clear and the user asked for handling/execution, continue after the plan comment is posted; formal plan approval is not required unless the user or repository instructions require it.

## Stage 3: Execution

Re-read the latest Issue comments and activities immediately before coding. Later explicit human decisions override the original Issue body and the plan.

Execution rules:

- Base new work on the repository default branch unless the Issue or repo instructions say otherwise.
- Create or use a feature branch; do not modify the default branch directly.
- Keep changes within the submitted plan's scope.
- Treat required documentation and contract updates as part of the implementation, not as post-merge cleanup.
- Update docs, API contracts, schemas, CLI help text, examples, migration notes, or skill instructions whenever user-visible behavior, public interfaces, configuration, workflows, or compatibility expectations change.
- If no documentation or contract update is needed, keep evidence for the PR body explaining why.
- Match existing project style and avoid unrelated refactors.
- Run the verification named in the plan, including doc/contract checks when applicable. If a command cannot run, record the exact reason.
- Keep evidence for the PR body: commands, outcomes, skipped checks, and residual risks.

Use the existing `cnb-code-commit` workflow as a reference for branch, commit, push, and PR mechanics, but this skill's plan-first requirement takes precedence.

## Stage 4: PR Creation

Create the PR body from `assets/pr-description.md`.

The PR must include:

- Summary of the change.
- Scope and out of scope.
- Documentation and contract changes, or why none were needed.
- Verification commands and outcomes.
- Risks and follow-up.
- A closing reference such as `Closes #<issue-number>`, `Fixes #<issue-number>`, or `Resolves #<issue-number>`.

After creating the PR, re-read it with verbose output and return the PR number, URL, source branch, verification summary, and any skipped checks. Do not merge.

## Stop Conditions

Stop and report the blocker when:

- The target repository or Issue number is ambiguous.
- A duplicate active PR or branch makes ownership unclear.
- Required Issue context, comments, or activities cannot be read.
- The Issue is too ambiguous to produce executable acceptance criteria.
- The documentation or contract impact is unclear enough that implementing would risk stale public behavior or incompatible contracts.
- Repository instructions require waiting for approval after the plan comment.
- Verification fails and the failure is not part of the intended fix.
- Push or PR creation fails.

For every CNB Issue comment or PR body you submit, append the current agent/model marker as the last non-empty line. Use actual current values in the format `Agent：<current-agent>，Model：<current-model>`; for example, `Agent：codex，Model：GPT-5.5`.
