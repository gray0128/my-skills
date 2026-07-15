# Verification And Closeout Reference

Load this reference when the required evidence is not obvious from project instructions and acceptance criteria.

## Select Evidence By Changed Surface

| Changed surface | Minimum meaningful evidence when applicable |
| --- | --- |
| Internal logic | focused tests for changed behavior and nearby regressions |
| Shared/public contract | contract validation, compatibility diff, provider/consumer or response-shape tests |
| Data or migration | migration check, compatibility across relevant versions, model/data tests |
| State or concurrency | successful transition, rejected transition, retry/failure, locking or idempotency where material |
| Generated artifacts | regeneration plus a no-drift check |
| Frontend/UI | follow active project instructions; type/build/browser checks only when required by acceptance or workflow |
| Deployment/runtime configuration | targeted config/startup/health evidence only when that surface changed |
| Permission or credential behavior | focused authorization, denial, redaction, or secret-handling checks only when that surface changed |

Use project-specific commands. Do not invent a broad verification suite when focused evidence is sufficient.

## Order Checks Efficiently

1. Run fast checks most likely to falsify the change.
2. Run required contract or compatibility gates.
3. Run broader integration or build checks only when the change surface or workflow requires them.
4. Stop once the completion bar is supported; do not add tool loops only to accumulate more evidence.

If a check fails, distinguish a defect in the change from an environmental failure or an unrelated baseline failure. Preserve exact evidence and avoid silently weakening acceptance criteria.

## Keep Release, Security, And Runtime Scope Light

Do not introduce canary plans, feature flags, threat models, supply-chain scans, deployment procedures, or production monitoring work unless the task or active project rules already place that surface in scope.

When one of those surfaces is in scope, use the project's established controls. In the absence of a baseline, perform only the smallest check needed for the accepted outcome and record the remaining gap.

## Reconcile Status Without Duplication

Choose one authoritative status source:

- Issue or task system for work state;
- PR for review and change scope;
- CI for verification outcome;
- contract artifact for stable interface behavior;
- deployment system for release state.

Repository progress Markdown may index these sources, but should not copy volatile details unless the project explicitly treats it as canonical.

## Closeout Evidence

Use a concise final structure:

```text
Outcome:
Contract impact:
Validation:
Status or commit:
Remaining gaps:
```

Use `Remaining gaps: none` only when all required evidence is complete. Distinguish `implemented`, `verified`, `committed`, `reviewed`, `merged`, and `deployed`; do not collapse them into a single done state.
