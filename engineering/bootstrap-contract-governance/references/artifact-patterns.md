# Compact Artifact Patterns

Use these patterns as content models, not required filenames.

## Source-Of-Truth Map

```text
Area:
Question answered:
Authoritative source:
Owner:
Generated or derived views:
Validation:
Known conflict or gap:
```

## Contract Entry

```text
Contract:
Provider:
Consumers:
Canonical artifact:
Compatibility rule:
Required verification:
Change authority:
Status:
```

## Minimal Project Control Section

```markdown
## Project Control Loop

- Follow the current work item from <authoritative tracker>.
- Read <canonical contract index or artifact> before changing stable behavior.
- Keep one independently verifiable delivery outcome in scope.
- Run <real validation commands> for the changed surface.
- Update <authoritative tracker> with actual status and evidence when authorized.
- Do not copy live Issue, PR, CI, or deployment state into secondary trackers.
```

## Verification Map

```text
Change surface:
Command or gate:
Evidence location:
When required:
Fallback if unavailable:
```

## Blocker Entry

```text
Blocked outcome:
Missing decision or dependency:
Evidence:
Owner or authority needed:
Safe work that can continue:
```

Avoid empty templates. Populate only the entries supported by current repository evidence.
