---
name: cnb-issue-create
description: Create clear, actionable CNB Issues from user requirements, bug reports, TAPD links, repository context, or planning notes. Use when Codex is asked to draft, open, submit, create, file, or register an Issue on CNB; to convert vague requirements into a structured CNB Issue; to check for duplicate open Issues before creation; or to prepare Issue metadata such as title, body, labels, assignees, priority, and acceptance criteria.
---

# CNB Issue Create

Use this skill to create one well-scoped CNB Issue. Do not implement the issue, open a PR, merge code, or close existing Issues from this skill.

## Core Workflow

1. Determine the target repository.
   - Prefer an explicit repo from the user.
   - Otherwise use `CNB_REPO_SLUG`.
   - If neither exists, infer from the current git remote only when unambiguous; otherwise ask for the repo.
2. Decide whether to create or only draft.
   - Create only when the user explicitly asks to create/open/submit/file the Issue.
   - If the user asks for a draft, return the draft and stop.
3. Gather just enough context.
   - Read user-provided text, linked files, logs, screenshots, and referenced docs.
   - For TAPD links, use the existing `cnb-tapd-resource-fetcher` workflow before drafting.
   - For repository-specific knowledge, use local docs first; use `cnb-repo-knowledge-base` only when live repository knowledge is needed.
4. Check for duplicate active work before creation.
   - List open Issues and compare title, keywords, affected modules, and acceptance criteria.
   - If a likely duplicate exists, report it and ask before creating a new Issue unless the user explicitly wants a separate Issue.
5. Draft the Issue body using `assets/issue-body-template.md`.
   - Keep scope small and testable.
   - Preserve uncertainty as explicit questions or assumptions.
   - Include acceptance criteria and verification evidence expected from the eventual implementer.
6. Create the Issue with CNB CLI.
   - Read `references/cnb-issue-commands.md` before constructing commands.
   - Use labels, assignees, priority, dates, and work mode only when provided or confidently inferred from repository convention.
7. Verify the created Issue.
   - Re-read the Issue with `--verbose`.
   - Confirm title, body, labels, assignees, priority, and links are correct.
   - Return the Issue number and URL.

## Scope Rules

- Prefer one Issue per independently verifiable outcome.
- Split unrelated bugs/features into separate Issues when their owners, risk, or acceptance criteria differ.
- Do not silently invent requirements. If the user request is ambiguous, write a short "Open Questions" section or ask before creation when the ambiguity changes the actual work.
- Do not add labels, assignees, priority, dates, or work mode unless the user requested them or the repository convention is clear.
- Do not create hidden/private Issues unless the user explicitly requests invisibility.
- Do not mention or summon NPC accounts unless the user requests that behavior.

## Handoff Contract

Write the Issue so a later `issue handling` skill can execute without reconstructing intent:

- `Background` explains why the work exists.
- `Scope` lists exactly what should change.
- `Out of Scope` prevents accidental expansion.
- `Acceptance Criteria` are observable pass/fail checks.
- `Verification` states commands, manual checks, or evidence required.
- `References` preserve source links, TAPD IDs, logs, screenshots, and related Issues.

For every CNB Issue body you create, append the current agent/model marker as the last non-empty line. Use actual current values in the format `Agent：<current-agent>，Model：<current-model>`; for example, `Agent：codex，Model：GPT-5.5`.
