# CNB Issue Plan Review Command Reference

## Read Issue Context

```bash
cnb issues get-issue --repo <group>/<repo> --number <issue> --verbose
cnb issues list-issue-comments --repo <group>/<repo> --number <issue> --verbose
cnb issues list-issue-activities --repo <group>/<repo> --number <issue> --verbose
cnb issues list-issues --repo <group>/<repo> --state open --page-size 50 --verbose
```

## Post Plan Review

```bash
cnb issues post-issue-comment \
  --repo <group>/<repo> \
  --number <issue> \
  --body '<issue-plan-review-body>' \
  --verbose
```
