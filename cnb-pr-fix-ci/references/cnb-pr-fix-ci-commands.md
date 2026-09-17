# CNB PR Fix CI Command Reference

Run command-specific `--help` when local CNB CLI behavior differs.

## Read PR Checks

```bash
cnb pulls get-pull --repo <group>/<repo> --number <pr> --verbose
cnb pulls list-pull-commit-statuses --repo <group>/<repo> --number <pr> --verbose
```

## Read Build Logs

Use status output to identify the build SN when available:

```bash
cnb build get-build-logs \
  --repo <group>/<repo> \
  --sha <head-sha> \
  --page-size 10 \
  --verbose

cnb build get-build-status \
  --repo <group>/<repo> \
  --sn <build-sn> \
  --verbose
```

Some CNB shortcut environments also provide:

```bash
cnb pulls get-ci-logs --sn <build-sn>
cnb pulls get-ci-timing --sn <build-sn>
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
git commit -m "fix: repair ci failure"
git push origin HEAD
```

## Post CI Fix Summary

```bash
cnb pulls post-pull-comment \
  --repo <group>/<repo> \
  --number <pr> \
  --body '<ci-fix-summary-body>' \
  --verbose
```
