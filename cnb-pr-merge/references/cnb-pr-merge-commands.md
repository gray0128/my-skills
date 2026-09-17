# CNB PR Merge Command Reference

Run command-specific `--help` when the local CNB CLI differs from these examples.

## Resolve Context

Prefer explicit user input, then environment:

```bash
echo "$CNB_REPO_SLUG"
echo "$CNB_PULL_REQUEST_IID"
echo "$CNB_DEFAULT_BRANCH"
```

If needed, infer the repository from `git remote -v` only when unambiguous.

## Read Live State

```bash
cnb pulls get-pull --repo <group>/<repo> --number <pr> --verbose
cnb pulls list-pull-reviews --repo <group>/<repo> --number <pr> --page-size 50 --verbose
cnb pulls list-pull-comments --repo <group>/<repo> --number <pr> --page-size 50 --verbose
cnb pulls list-pull-commits --repo <group>/<repo> --number <pr> --verbose
cnb pulls list-pull-commit-statuses --repo <group>/<repo> --number <pr> --verbose
```

For linked Issues:

```bash
cnb issues get-issue --repo <group>/<repo> --number <issue> --verbose
cnb issues list-issue-activities --repo <group>/<repo> --number <issue> --verbose
```

For source branch cleanup evidence:

```bash
git ls-remote --heads origin <source-branch>
git branch --list <source-branch>
```

An empty result means the branch is absent.

## Merge

Use an explicit merge style when the user or repository policy specifies one. The merge commit message must preserve closing keywords for all linked Issues:

```bash
cnb pulls merge-pull \
  --repo <group>/<repo> \
  --number <pr> \
  --merge-style <merge|squash|rebase> \
  --commit-title '<title>' \
  --commit-message 'Closes #<issue>

<summary>

Agent：codex，Model：GPT-5' \
  --verbose
```

When no style is specified, first try omitting `--merge-style`:

```bash
cnb pulls merge-pull \
  --repo <group>/<repo> \
  --number <pr> \
  --commit-title '<title>' \
  --commit-message '<message>' \
  --verbose
```

If CNB rejects the request because `merge_style` is required, retry with `--merge-style merge`.

## Post-Merge Verification

```bash
cnb pulls get-pull --repo <group>/<repo> --number <pr> --verbose
cnb issues get-issue --repo <group>/<repo> --number <issue> --verbose
cnb issues list-issue-activities --repo <group>/<repo> --number <issue> --verbose
git ls-remote --heads origin <source-branch>
git pull --ff-only origin <default-branch>
```

## Linked Issue Auto-Close Verification

After merge, verify linked Issues closed automatically:

```bash
cnb issues get-issue --repo <group>/<repo> --number <issue> --verbose
cnb issues list-issue-activities --repo <group>/<repo> --number <issue> --verbose
```

If a linked Issue is still open, stop and report that CNB auto-close did not occur. Do not run manual close commands unless the active user explicitly authorizes manual closure.

Manual closure, only after explicit authorization:

```bash
cnb issues update-issue \
  --repo <group>/<repo> \
  --number <issue> \
  --state closed \
  --state-reason completed \
  --verbose

cnb issues get-issue --repo <group>/<repo> --number <issue> --verbose
cnb issues list-issue-activities --repo <group>/<repo> --number <issue> --verbose
```

## Source Branch Cleanup

Delete only same-repo PR source branches. Never delete the default/base branch, protected branches, or fork branches from this workflow.

Remote branch cleanup:

```bash
cnb git delete-branch \
  --repo <group>/<repo> \
  --branch <source-branch> \
  --verbose

git ls-remote --heads origin <source-branch>
```

Local branch cleanup after switching to the updated default branch:

```bash
git checkout <default-branch>
git pull --ff-only origin <default-branch>
git branch --list <source-branch>
git branch -d <source-branch>
git branch --list <source-branch>
```

If `git branch -d` refuses because the branch is not merged, stop and report the blocker. Do not use `-D` unless the user explicitly authorizes force deletion.

For main push CI:

```bash
cnb build get-build-logs \
  --repo <group>/<repo> \
  --sha <merge-sha> \
  --event push \
  --page-size 10 \
  --verbose

cnb build get-build-status \
  --repo <group>/<repo> \
  --sn <build-sn> \
  --verbose
```

If there is no main push pipeline by repository design, record `Main CI: not_required` with evidence from repository instructions or absent pipeline configuration.

## Closeout Comment

Post a closeout comment when useful evidence is missing from the Issue or PR, repository instructions require it, Issue auto-close failed, or branch cleanup was performed:

```bash
cnb issues post-issue-comment \
  --repo <group>/<repo> \
  --number <issue> \
  --body '<merge-closeout-body>'
```

Remote/local source branch cleanup is expected after a successful merge when same-repo source branches remain present. Manual Issue closure is not expected by default; record any auto-close failure and only close manually after explicit authorization.
