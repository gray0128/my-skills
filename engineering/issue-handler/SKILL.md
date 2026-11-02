---
name: issue-handler
description: Generic issue-to-PR workflow for coding agents. Use when the user asks to process, handle, implement, fix, continue, or choose an issue from GitHub, CNB, GitLab, Jira-backed repos, or similar issue trackers; when an issue needs live context intake, an issue plan comment before code changes, implementation, verification, and a PR/merge request with agent and model attribution.
---

# Issue Handler

## Core Rule

Process an issue from live tracker state to a verified PR/MR. Before implementation, gather necessary context and post the proposed handling plan as an issue comment. Append the actual coding agent and model marker as the final non-empty line of both the issue plan comment and the PR/MR description:

```text
Agent: <coding agent name> · Model: <model name>
```

This marker identifies the tool and model performing the work, not any project-defined agent role.

## Workflow

1. Identify the issue and platform.
   - Prefer platform-native tooling already configured for the repo: `gh` or GitHub APIs for GitHub, `cnb` for CNB, `glab` for GitLab, tracker APIs/CLI for others.
   - If no issue number is specified, read the live open issue list, milestones/labels, open PRs/MRs, and branch state; choose one issue only when the selection is clearly justified.
   - Verify whether the target is actually an issue, PR/MR, or another tracker object before acting.

2. Gather necessary information before implementation.
   - Read the issue title, body, labels, assignee, milestone, linked tasks, linked PRs/MRs, and all relevant comments.
   - Read repository instructions such as `AGENTS.md`, `CONTRIBUTING`, task plans, contracts, API docs, and relevant design docs.
   - Inspect current branch, remote branches, open PRs/MRs, and any existing work for the same issue.
   - Locate affected code using the repo's preferred code intelligence or search workflow.
   - Identify the required verification commands from docs, CI config, package scripts, or project conventions.

3. Post an issue plan comment before editing code.
   - Use `assets/issue-plan-comment-template.md` as the structure unless the repository already has a stricter template.
   - Keep the plan scoped to one independently verifiable slice.
   - Include: context gathered, assumptions, proposed change, affected files/areas, verification plan, risks or open questions.
   - End with the exact agent/model marker line.
   - Do not start implementation until the comment has been submitted successfully, unless the user explicitly requested a local-only draft or the tracker is inaccessible. If the tracker is inaccessible, stop and report the blocker.

4. Implement surgically.
   - Create or switch to an appropriate issue branch if needed.
   - Update contracts/docs first when the change affects external behavior, APIs, schemas, policies, state machines, security semantics, or persistence models.
   - Keep the diff limited to the accepted plan. If new information changes scope materially, post a follow-up issue comment before expanding implementation.
   - Do not merge unless the user explicitly authorizes it or the repo's automation policy requires it.

5. Verify.
   - Run the verification commands identified during intake.
   - If a command cannot run, record the exact reason and the residual risk.
   - Re-check live issue/PR state before publishing if the branch or issue may have changed while working.

6. Open or update the PR/MR.
   - Use `assets/pr-description-template.md` as the default description template unless the repository has its own PR template.
   - Include issue link, summary, implementation notes, verification results, risks, and any skipped checks.
   - End with the exact agent/model marker line.
   - After publishing, comment or update the issue/PR with the verification result when the repository workflow expects it.

## Agent and Model Attribution

Use the current runtime's actual identity. Examples:

```text
Agent: codex desktop · Model: GPT-5.5
Agent: Claude Code · Model: Claude Sonnet 4.5
Agent: GitHub Copilot coding agent · Model: GPT-5
```

If the exact model is unavailable, use the most precise truthful value available, such as `Model: unknown`. Do not invent a model version.

## Templates

- `assets/issue-plan-comment-template.md`: copy when posting the required pre-implementation issue comment.
- `assets/pr-description-template.md`: copy when creating or updating the PR/MR description.

Adapt template language to the issue/repo language. Keep the final agent/model marker as the last non-empty line.
