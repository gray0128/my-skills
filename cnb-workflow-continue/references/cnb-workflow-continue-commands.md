# CNB Workflow Continue Command Reference

## Issue State

```bash
cnb issues get-issue --repo <group>/<repo> --number <issue> --verbose
cnb issues list-issue-comments --repo <group>/<repo> --number <issue> --verbose
cnb issues list-issue-activities --repo <group>/<repo> --number <issue> --verbose
cnb issues list-issues --repo <group>/<repo> --state open --page-size 50 --verbose
```

## PR State

```bash
cnb pulls get-pull --repo <group>/<repo> --number <pr> --verbose
cnb pulls list-pull-comments --repo <group>/<repo> --number <pr> --page-size 50 --verbose
cnb pulls list-pull-reviews --repo <group>/<repo> --number <pr> --page-size 50 --verbose
cnb pulls list-pull-commits --repo <group>/<repo> --number <pr> --verbose
cnb pulls list-pull-files --repo <group>/<repo> --number <pr> --verbose
cnb pulls list-pull-commit-statuses --repo <group>/<repo> --number <pr> --verbose
```

## Branch And CI State

```bash
git ls-remote --heads origin <source-branch>
cnb build get-build-logs --repo <group>/<repo> --sha <sha> --page-size 10 --verbose
cnb build get-build-status --repo <group>/<repo> --sn <build-sn> --verbose
```
