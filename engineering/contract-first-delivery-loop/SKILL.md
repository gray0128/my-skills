---
name: contract-first-delivery-loop
description: >
  Use when the user explicitly invokes this skill to execute or continue one tracked implementation slice in a repository that already has authoritative contracts and work tracking. Deliver one independently verifiable, contract-governed outcome by resolving active instructions and sources of truth, defining completion and compatibility, analyzing affected consumers, implementing in-scope changes, running risk-based validation, reconciling the authoritative tracker, and reporting evidence. Do not use to install governance, audit governance, perform read-only review, or handle ordinary untracked coding.
---

# Contract-First Delivery Loop

## Goal

Deliver one tracked implementation outcome whose code, canonical contract, required validation, and authoritative work status agree.

Define the destination and completion bar, then choose the smallest efficient path. Do not narrate or mechanically repeat this workflow when the task is already clear.

## Precedence And Authority

Apply instructions in this order:

1. Current user instructions and authorization.
2. Active repository guidance such as `AGENTS.md`, including closer subtree overrides.
3. Project-declared canonical contracts, work tracker, and engineering workflow.
4. This skill's defaults.

Do not use recency alone to decide which artifact is authoritative. When code, tests, prose, schemas, and trackers disagree, identify their declared roles before editing.

## Establish The Task Contract

Before editing, resolve enough evidence to define:

```text
Outcome:
Acceptance criteria:
Authoritative work item:
Canonical contract artifacts:
Contract delta and compatibility:
Affected consumers:
Allowed actions:
Out of scope:
Required validation:
Stop conditions:
```

Keep this task contract internal for straightforward work. Show it briefly when the task is long, ambiguous, high-impact, or benefits from user verification.

If the user names a task, use it. If the user says only "continue", select the next unfinished item only when the authoritative tracker yields one unblocked, unambiguous candidate. Ask for direction when candidates conflict or require materially different outcomes.

## Bound One Deliverable Outcome

Treat API, CLI, internal interface, data, state, permission, and other contract classes as risk tags, not automatic task boundaries.

Keep related cross-layer changes together when they form one independently understandable and verifiable vertical slice. Split work when a part can be delivered independently, requires separate authorization, has a different rollback boundary, or would leave the repository inconsistent between changes.

Avoid adjacent refactors and speculative abstractions unless they are required to meet the acceptance criteria.

## Resolve Contract Intent

Use a machine-readable artifact as the shape authority only when the project declares it canonical. Load `references/contract-and-compatibility.md` when the task changes a shared or published interface, schema, generated artifact, state vocabulary, or consumer-visible behavior.

Apply these decision rules:

- For an implementation defect, make implementation conform to the accepted contract.
- For an intentional published-contract change, update the canonical artifact before or in the same atomic change as dependent implementation and tests.
- For a discovered contract conflict, classify whether the contract is stale, the implementation is wrong, or intent changed; do not silently choose.
- For exploratory work, avoid changing accepted contract status until the experiment establishes a decision.
- For a breaking change, require an explicit versioning, migration, compatibility-window, or acceptance decision before depending on the new behavior.

## Analyze Proportionately

Run impact analysis when the change touches shared symbols, public contracts, data models, state semantics, generated consumers, or unfamiliar cross-module behavior.

Use the repository's configured code-intelligence tool first when available and applicable. Otherwise use targeted searches for callers, consumers, schemas, stable codes, and generated outputs. Stop once the affected surface and validation needs are sufficiently supported.

Report a material blast-radius finding before editing when it changes the task boundary, compatibility plan, or required authorization.

## Implement The Slice

- Follow existing local patterns and accepted contract semantics.
- Preserve unrelated dirty or untracked files.
- Change generated artifacts only when the project tracks them or a required gate checks them.
- Keep contract, implementation, tests, and intentional generated outputs in one coherent change when separating them would break the repository.
- Do not broaden a code task into PR creation, merge, release, deployment, or external communication without user or repository-workflow authorization.

## Verify By Risk

Run the narrowest meaningful validation that can establish the acceptance criteria. Load `references/verification-and-closeout.md` when verification is unclear or the change touches shared contracts, schemas, data, state, generated consumers, or multiple modules.

Prefer focused checks before broader checks. Respect explicit project rules that narrow or skip validation, including UI workflows that request modification without inspection. Do not add release, security, or runtime verification merely because this skill is active; apply those checks only when the changed surface or accepted task explicitly requires them.

If required validation cannot run, record the exact gap and the closest meaningful evidence. Do not mark the task done when a required gate is missing or failing.

## Reconcile One Source Of Status

Update the authoritative work item with actual state and concise evidence when the user or repository workflow authorizes that write.

Avoid duplicating live Issue, PR, CI, or deployment state into Markdown trackers. Prefer links or identifiers for durable external evidence. Update repository documentation only when it is itself canonical or the accepted behavior changed.

Create a local commit only when requested or required by the active workflow. Treat PR creation, merge, release, deployment, and external comments as separate side effects unless already authorized.

## Completion Bar

Close the task only when:

- the requested outcome is implemented;
- implementation and canonical contract agree;
- required validation passes or an explicitly accepted gap is recorded;
- the authoritative work status reflects reality when reconciliation is in scope;
- residual risks and deferred work are named without being silently included.

Report the outcome, changed contract behavior, exact validation evidence, tracker/commit result when applicable, and remaining gaps. Lead with what is complete.

## Stop Conditions

Stop and request direction only when safe progress cannot continue because:

- no authoritative task or contract can be resolved;
- equally plausible sources prescribe materially different behavior;
- a breaking change lacks an accepted compatibility or migration decision;
- required external, destructive, costly, or scope-expanding authority is missing;
- unrelated user changes overlap the required edit surface;
- validation reveals a materially larger task than the accepted boundary.
