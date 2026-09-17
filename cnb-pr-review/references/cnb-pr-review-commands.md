# CNB PR Review Command Reference

Run command-specific `--help` when the local CNB CLI differs from these examples.

## Resolve Context

Prefer explicit user input, then environment:

```bash
echo "$CNB_REPO_SLUG"
echo "$CNB_PULL_REQUEST_IID"
echo "$CNB_PULL_REQUEST_SHA"
echo "$CNB_PULL_REQUEST_TARGET_SHA"
echo "$CNB_BUILD_USER"
```

If needed, infer the repository from `git remote -v` only when unambiguous.

## Current Review User

Determine the current CNB review user before choosing `approve` or `request_changes`:

```bash
cnb users get-user-info --verbose
```

When running inside CNB automation, also inspect available event/user variables:

```bash
echo "$CNB_BUILD_USER"
echo "$CNB_BUILD_USER_NICKNAME"
echo "$CNB_BUILD_USER_ID"
```

Compare that identity with the PR author from `cnb pulls get-pull --verbose`. If the PR author and current review user match, use comment-only submission unless repository instructions explicitly allow the single-maintainer exception.

## PR Intake

```bash
cnb pulls get-pull --repo <group>/<repo> --number <pr> --verbose
cnb pulls list-pull-comments --repo <group>/<repo> --number <pr> --verbose
cnb pulls list-pull-reviews --repo <group>/<repo> --number <pr> --verbose
cnb pulls list-pull-commits --repo <group>/<repo> --number <pr> --verbose
cnb pulls list-pull-files --repo <group>/<repo> --number <pr> --verbose
cnb pulls list-pull-commit-statuses --repo <group>/<repo> --number <pr> --verbose
```

If check output is unclear, inspect CLI help for the local command names:

```bash
cnb pulls --help
```

## Linked Issue Context

For each linked Issue:

```bash
cnb issues get-issue --repo <group>/<repo> --number <issue> --verbose
cnb issues list-issue-comments --repo <group>/<repo> --number <issue> --verbose
cnb issues list-issue-activities --repo <group>/<repo> --number <issue> --verbose
```

Prefer the latest explicit human decision when Issue text, comments, and PR text conflict.

## Diff Inspection

Fetch base and head if the commits are not already local:

```bash
git fetch origin <base-branch> <head-branch>
```

Inspect the exact range:

```bash
git diff --name-only <base-sha>...<head-sha>
git diff --stat <base-sha>...<head-sha>
git diff -U5 <base-sha>...<head-sha>
git diff -U5 <base-sha>...<head-sha> -- <path>
```

For code review, filter low-signal generated or binary artifacts unless they are the point of the PR:

```bash
git diff -U5 <base-sha>...<head-sha> -- . \
  ':!package-lock.json' ':!yarn.lock' ':!pnpm-lock.yaml' ':!go.sum' ':!*.lock' \
  ':!*.png' ':!*.jpg' ':!*.gif' ':!*.svg' ':!*.ico' \
  ':!*.min.js' ':!*.min.css' ':!*.map' \
  ':!dist/*' ':!build/*' ':!node_modules/*'
```

## Submit Formal Review

Use `approve`, `request_changes`, or `comment` according to the review result:

```bash
cnb pulls post-pull-review \
  --repo <group>/<repo> \
  --number <pr> \
  --event <approve|request_changes|comment> \
  --body '<review-body>' \
  --verbose
```

Apply the author gate before using `approve` or `request_changes`:

- Different PR author and review user: use `approve` or `request_changes` according to the review result.
- Same PR author and review user with explicit single-maintainer exception: use `--event comment`, set `Review Submission: single_maintainer_comment`, and record the exception.
- Same PR author and review user without explicit exception: use `--event comment`, set `Review Submission: author_self_comment`, and state that the result is not formal approval.
- Unknown review user: do not approve; use `--event comment` and explain identity could not be verified.

For actionable line-level findings, pass repeated comment fields in the same review. Line numbers must refer to the new/right side unless commenting on removed code:

```bash
cnb pulls post-pull-review \
  --repo <group>/<repo> \
  --number <pr> \
  --event request_changes \
  --body '<review-body>' \
  --comments-body '<finding-body>' \
  --comments-path '<path>' \
  --comments-start-line <line> \
  --comments-start-side right \
  --comments-end-line <line> \
  --comments-end-side right \
  --comments-subject-type line \
  --verbose
```

If formal review submission is unavailable but a comment is still useful:

```bash
cnb pulls post-pull-comment \
  --repo <group>/<repo> \
  --number <pr> \
  --body '<review-body-or-submission-failure-summary>'
```

Do not treat an ordinary comment as formal approval unless repository policy explicitly defines and records that exception.
