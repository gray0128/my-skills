---
name: cnb-pr-address-review
description: Address CNB PR review feedback after a PR receives comments, requested changes, or blocking review findings. Use when Codex is asked to handle review comments, fix requested changes, respond to PR feedback, update a PR after review, or push follow-up commits for a CNB PR. Reads live PR reviews/comments, classifies feedback, applies only approved/actionable fixes including required docs/contracts, pushes to the existing PR branch, and requests a fresh review for the new head SHA.
---

# CNB PR Address Review

Use this skill to respond to review feedback on an existing CNB PR. Do not perform the independent review itself, merge the PR, close Issues, or broaden scope beyond accepted feedback.

## Workflow

1. Resolve the repository and PR number.
2. Read live PR metadata, comments, formal reviews, commits, files, checks, linked Issues, and latest head SHA.
3. Classify feedback as `blocking`, `accepted_nonblocking`, `discussion`, `stale`, or `out_of_scope`.
4. Stop for clarification when requested changes conflict with Issue scope, the submitted plan, or later human decisions.
5. Switch to the PR source branch and pull the latest branch state.
6. Apply only accepted/actionable fixes. Include docs/contracts when feedback or code changes affect public behavior, APIs, schemas, CLI help, configuration, pipelines, or skill instructions.
7. Run focused verification.
8. Commit, push to the existing PR branch, and post a PR update comment using `assets/review-feedback-response.md`.
9. Require a fresh review for the new head SHA.

Read `references/cnb-pr-address-review-commands.md` before constructing CNB or git commands.

## Rules

- Treat formal `request_changes` findings as blocking unless superseded by a later human decision.
- Do not fix stale findings that target an older head SHA unless they still apply.
- Do not implement new features discovered during review; ask for a new Issue or explicit scope expansion.
- Do not use `git add -A` when unrelated local changes exist.
- Do not force-push unless the user explicitly authorizes it.
- Do not claim review is resolved; state what was changed and request re-review.

## Stop Conditions

Stop and report the blocker when:

- The target PR or source branch is ambiguous.
- Feedback conflicts or the intended fix would exceed Issue/PR scope.
- The PR head changes while you are preparing fixes.
- The source branch cannot be checked out or updated safely.
- Verification fails for reasons unrelated to the intended fix.
- Push fails.

For every CNB PR comment you submit, append the current agent/model marker as the last non-empty line. Use actual current values in the format `Agent：<current-agent>，Model：<current-model>`; for example, `Agent：codex，Model：GPT-5.5`.
