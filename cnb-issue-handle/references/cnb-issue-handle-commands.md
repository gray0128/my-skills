# CNB Issue Handle Command Reference

Run command-specific `--help` when the local CNB CLI differs from these examples.

## Resolve Context

Prefer explicit user input, then environment:

```bash
echo "$CNB_REPO_SLUG"
echo "$CNB_ISSUE_IID"
echo "$CNB_DEFAULT_BRANCH"
```

If needed, infer the repository from `git remote -v` only when unambiguous.

## Issue Intake

```bash
cnb issues get-issue --repo <group>/<repo> --number <issue> --verbose
cnb issues list-issue-comments --repo <group>/<repo> --number <issue> --verbose
cnb issues list-issue-activities --repo <group>/<repo> --number <issue> --verbose
cnb issues list-issues --repo <group>/<repo> --state open --page-size 50 --verbose
```

Post the implementation plan before coding:

```bash
cnb issues post-issue-comment \
  --repo <group>/<repo> \
  --number <issue> \
  --body '<plan-markdown>'
```

## Existing PR Or Branch Check

Use CNB CLI or repository search to identify existing work for the Issue before creating a branch. Look for:

- PR title or body containing `#<issue>`, `Closes #<issue>`, `Fixes #<issue>`, or `Resolves #<issue>`.
- Branch names that include the Issue number or the same concise keywords.
- Issue comments that link an active PR.

## Branch, Commit, Push

Use the repository's default branch unless project instructions specify another base:

```bash
git fetch origin <default-branch>
git checkout <default-branch>
git pull --ff-only origin <default-branch>
git checkout -b <feature-branch>
```

Suggested branch shape:

```text
auto/<issue-number>-<short-topic>
```

After implementation and verification:

```bash
git diff --stat
git status --short
git add <changed-files>
git commit -m "<type>: <short summary>"
git push origin HEAD
```

Avoid `git add -A` when unrelated local changes exist.

## PR Creation

```bash
cnb pulls post-pull \
  --repo <group>/<repo> \
  --base <default-branch> \
  --head <feature-branch> \
  --title '<type>: <short summary>' \
  --body '<pr-body-from-template>' \
  --verbose
```

Then verify:

```bash
cnb pulls get-pull --repo <group>/<repo> --number <pr> --verbose
```

Do not merge from this workflow.
