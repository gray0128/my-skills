# CNB PR Address Review Command Reference

Run command-specific `--help` when local CNB CLI behavior differs.

## Read PR Feedback

```bash
cnb pulls get-pull --repo <group>/<repo> --number <pr> --verbose
cnb pulls list-pull-reviews --repo <group>/<repo> --number <pr> --page-size 50 --verbose
cnb pulls list-pull-comments --repo <group>/<repo> --number <pr> --page-size 50 --verbose
cnb pulls list-pull-commits --repo <group>/<repo> --number <pr> --verbose
cnb pulls list-pull-files --repo <group>/<repo> --number <pr> --verbose
cnb pulls list-pull-commit-statuses --repo <group>/<repo> --number <pr> --verbose
```

For linked Issues:

```bash
cnb issues get-issue --repo <group>/<repo> --number <issue> --verbose
cnb issues list-issue-comments --repo <group>/<repo> --number <issue> --verbose
cnb issues list-issue-activities --repo <group>/<repo> --number <issue> --verbose
```

## Update PR Branch

```bash
git fetch origin <source-branch>
git checkout <source-branch>
git pull --ff-only origin <source-branch>
git status --short
```

After fixes:

```bash
git diff --stat
git status --short
git add <changed-files>
git commit -m "fix: address review feedback"
git push origin HEAD
```

## Post Update Comment

```bash
cnb pulls post-pull-comment \
  --repo <group>/<repo> \
  --number <pr> \
  --body '<review-feedback-response-body>' \
  --verbose
```
