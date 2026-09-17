---
name: cnb-pr-merge
description: Merge CNB pull requests only after explicit human authorization, live readiness validation, current head-SHA review evidence, successful checks, linked Issue verification, linked-Issue auto-close verification, remote/local source branch cleanup, and post-merge CI verification. Use when Codex is asked to merge, complete, land, close out, or verify a CNB PR after review; to handle single-maintainer commented review evidence; to run CNB merge-pull safely; or to verify merged PR state, linked Issue state, source branch cleanup, and main-branch CI.
---

# CNB PR Merge

Use this skill to merge one CNB PR and verify closeout. Do not use it to implement fixes, perform the original PR review, approve your own review, or create new Issues.

## Hard Gate

Never merge unless the user explicitly authorizes merge in the active conversation. Past approval, PR comments, labels, or phrases in the PR body are not enough.

## Workflow

1. Resolve the repository and PR number.
2. Read live PR, review, CI, Issue, branch, and repository-policy context.
3. Build a readiness record using `assets/merge-readiness.md`.
4. Stop if any readiness condition fails.
5. Run `cnb pulls merge-pull` with the chosen merge style and a merge commit message that preserves linked-Issue closing keywords.
6. Verify closeout, ensure linked Issues auto-closed, delete the same-repo source branch remotely and locally, and submit `assets/merge-closeout-comment.md` when useful evidence is missing from the Issue or PR.

Read `references/cnb-pr-merge-commands.md` before constructing CNB or git commands.

## Readiness Checks

Immediately before merge, verify all of the following from live CNB/git state:

- Explicit human merge authorization exists in the current conversation.
- PR is open, not WIP/draft, unblocked, and mergeable.
- Current head SHA matches the latest valid review evidence.
- No newer review requests changes or reports blockers.
- Required PR checks are successful or explicitly not required by repository policy.
- PR title or body links intended Issues when Issue closeout is expected; identify exact Issue numbers before merging.
- Merge commit title or message will include closing keywords for every linked Issue, such as `Closes #<issue>`, `Fixes #<issue>`, or `Resolves #<issue>`.
- Merge style is specified by the user, repository policy, or safely omitted to use CNB defaults.
- Repository instructions do not require another gate.

## Review Evidence

Prefer formal CNB Pull Review approval. Accept single-maintainer commented review evidence only when repository instructions or the current user explicitly allow that workflow and the evidence records:

- Review result is approved or review-clean.
- Blocking issues are zero.
- Review evidence targets the current PR head SHA.
- Submission is `single_maintainer_comment` or equivalent explicit single-maintainer comment evidence.
- The PR author/review user self-review limitation is documented.
- Current checks are successful.

Do not treat `author_self_comment`, ordinary discussion, `LGTM`, or unstructured comments as approval evidence unless repository policy explicitly defines that exception.

## Merge Execution

Use `cnb pulls merge-pull`. If the user or repository specifies `merge`, `squash`, or `rebase`, pass it explicitly. If no style is specified and the repository has no policy, omit `--merge-style` first and let CNB use its default; if the CNB API rejects a missing `merge_style`, retry with `--merge-style merge`.

The merge commit message must include closing keywords for every linked Issue. Do not replace `Closes #<issue>` with weaker text such as `Issue #<issue>`, because CNB may mention the Issue without closing it. Append the current agent/model marker as the last non-empty line. Use actual current values in the format `Agent：<current-agent>，Model：<current-model>`; for example, `Agent：codex，Model：GPT-5.5`.

If the PR body has closing keywords and you pass a custom `--commit-message`, copy those closing keywords into the merge commit message.

## Closeout

After merge, verify:

- PR is closed/merged and record the merge commit.
- Linked Issues reached `closed` with completed state when the PR used closing keywords or repository policy expects automatic closeout.
- If a linked Issue remains open after merge, stop and report the auto-close failure unless the active user explicitly authorizes manual Issue closure. Do not silently close Issues with commands by default.
- Same-repo source branch is deleted remotely after successful merge. Do not delete fork branches or protected/default/base branches.
- Local source branch is deleted after switching away from it and after it is merged into the updated default branch. Use normal deletion only; do not force delete unless the user explicitly authorizes it.
- Local default branch is updated to the merge commit.
- Main-branch push CI for the merge commit reaches success when repository policy treats main CI as part of completion.

Branch cleanup is part of this workflow after successful merge. Issue closeout should happen through CNB auto-close from closing keywords; manual Issue closure requires explicit active-conversation authorization after auto-close fails. Stop if Issue auto-close fails without that authorization, branch cleanup fails, the branch is not a same-repo PR source branch, the branch is protected/default/base, or normal local branch deletion is unsafe.

For every CNB closeout comment you submit, append the current agent/model marker as the last non-empty line. Use actual current values in the format `Agent：<current-agent>，Model：<current-model>`; for example, `Agent：codex，Model：GPT-5.5`.

## Stop Conditions

Stop and report the blocker when:

- The user has not explicitly authorized merge in the active conversation.
- The target repo or PR number is ambiguous.
- Live PR, review, check, or linked Issue state cannot be read.
- PR head SHA differs from the latest valid review evidence.
- Required checks fail or are still pending.
- A newer review requests changes or reports a blocker.
- Review evidence is only author-self comment and no single-maintainer policy allows it.
- Merge fails.
- Expected post-merge Issue closeout, remote source branch deletion, local source branch deletion, local main update, or main-CI closeout cannot be verified.

Never claim completion while required main CI or configured cleanup is red, pending, or unknown.
