# CNB Issue Command Reference

Use `cnb issues create-issue` for creation. Run `cnb issues create-issue --help` when a field or CLI version is uncertain.

## Resolve Repository

Prefer:

```bash
echo "$CNB_REPO_SLUG"
```

If empty, inspect the git remote and derive `<group>/<repo>` only when the result is obvious.

## Duplicate Check

```bash
cnb issues list-issues \
  --repo <group>/<repo> \
  --state open \
  --page-size 50 \
  --verbose
```

Treat an Issue as a likely duplicate when it has the same affected area and substantially the same expected outcome, even if the title differs.

## Create Issue

For a simple body, pass the Markdown directly:

```bash
cnb issues create-issue \
  --repo <group>/<repo> \
  --title '<issue-title>' \
  --body '<markdown-body>' \
  --verbose
```

Optional fields:

```bash
--labels <label>
--assignees <username>
--priority <P0|P1|P2|P3|-1P|-2P>
--start-date <YYYY-MM-DD>
--end-date <YYYY-MM-DD>
--work-mode
--invisible
```

Repeat `--labels` and `--assignees` for multiple values. CNB currently limits labels to 10 and assignees to 8.

For complex multiline content, use `--data @<json-file>` if quoting would be fragile. Keep JSON keys aligned with the CLI field names shown by `cnb issues create-issue --help`.

## Verify Creation

After creation, re-read the Issue:

```bash
cnb issues get-issue \
  --repo <group>/<repo> \
  --number <issue-number> \
  --verbose
```

If metadata was omitted at creation and must be added later, use the dedicated Issue commands rather than recreating the Issue:

```bash
cnb issues post-issue-labels --repo <group>/<repo> --number <issue-number> --labels <label>
cnb issues post-issue-assignees --repo <group>/<repo> --number <issue-number> --assignees <username>
```

## Attachments

If the Issue needs local screenshots or files and create-time upload helpers are unavailable or unclear, create the Issue first, then upload/attach files through the existing `cnb-upload-attachment` workflow in a follow-up Issue comment.
