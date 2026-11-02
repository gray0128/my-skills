---
name: audit-contract-governance
description: >
  Use when the user explicitly invokes this skill to perform a read-only, evidence-based audit of a software repository's contract governance. Inspect active instructions, declared sources of truth, contracts, compatibility rules, work tracking, verification gates, and contradictions; distinguish observed facts from inference; and report prioritized strengths, gaps, and minimal recommendations with exact evidence. Do not edit files, update trackers, post comments, implement fixes, install governance, or expand into release, security, and runtime review unless the user explicitly places those surfaces in audit scope.
---

# Audit Contract Governance

## Goal

Determine whether the repository can guide a contributor or coding agent from an accepted contract and tracked task to a verifiable completion without relying on conflicting or duplicated sources of truth.

Lead with the audit conclusion and material evidence. Do not turn the audit into implementation.

## Hard Read-Only Boundary

Use only non-mutating inspection and diagnostic commands. Do not:

- edit or create repository files;
- update Issue, task, PR, CI, or deployment state;
- post comments or reviews;
- create commits, branches, PRs, releases, or deployments;
- install governance controls or fix findings.

If the user asks to audit and fix, complete the audit first and separate any later mutation into `bootstrap-contract-governance` or `contract-first-delivery-loop` with the required authorization.

## Precedence And Evidence

Apply current user scope first, then active repository guidance, then declared project authorities, then this skill's defaults.

For every material conclusion, distinguish:

- Observed: directly supported by a file, command, tracker, schema, or test result.
- Inferred: a conclusion derived from several observed facts.
- Missing: evidence expected by the declared workflow but not found.
- Conflicted: two plausible authorities prescribe different facts or behavior.

Do not treat the newest file as authoritative unless the project says recency decides authority.

## Establish The Audit Contract

Resolve and, when useful, state:

```text
Audit scope:
Repository or module boundary:
Questions to answer:
Evidence sources:
Excluded surfaces:
Output depth:
Stop conditions:
```

Default to repository-local contract and delivery governance. Exclude production operations, release administration, security architecture, and runtime reliability unless explicitly requested or necessary to understand a contract already in scope.

## Inspect Proportionately

Follow the repository's discovery rules. When a configured code graph or index exists, use it before broad text search for code relationships. Otherwise use targeted file and text inspection.

Inspect enough evidence to answer:

1. Which instructions govern work at this path?
2. Which artifact defines each important stable behavior or interface?
3. Which system records current work state?
4. How are contract changes and compatibility decisions controlled?
5. Which checks prove implementation conforms to the contract?
6. Can one tracked task be selected, bounded, verified, and closed without contradictory guidance?
7. Which live or generated facts are unnecessarily copied into secondary documents?

Sample representative contracts and workflows. Do not exhaustively read unrelated modules after the conclusion is supported.

## Evaluate The Control System

Load `references/audit-rubric.md` for dimensions and severity guidance.

Assess:

- authority and instruction clarity;
- canonical contract coverage;
- structured or executable contract evidence where justified;
- compatibility and consumer awareness;
- task boundary and completion rules;
- verification and CI enforcement;
- status traceability and duplication;
- contradictions, stale references, and unowned decisions.

Do not penalize a small repository for lacking enterprise controls it does not need. Judge governance against actual project risk and declared workflow.

## Challenge Claims

- A Markdown file named `contract` is not automatically canonical or executable.
- A schema is not governed merely because it exists.
- Passing unit tests do not prove consumer compatibility unless they exercise that boundary.
- A progress page is not current merely because it has a recent timestamp.
- An additive change is not automatically backward compatible.
- A documented command is not evidence that CI or contributors actually run it.
- More files and states do not necessarily mean stronger governance.

Use absence carefully. Report that evidence was not found within the inspected scope, not that a capability definitively does not exist elsewhere.

## Prioritize Findings

Prioritize concrete failure modes over completeness preferences. A finding should include:

```text
Severity:
Observed evidence:
Why it matters:
Likely failure mode:
Minimal recommendation:
Affected scope:
```

Do not assign severity based only on document count or stylistic preference. Combine related symptoms that share one root cause.

## Report

Load `references/report-template.md` when the user requests a formal report or the audit has several findings.

Return:

- overall conclusion;
- controls that are already effective;
- prioritized findings with exact paths, sections, commands, or live-source identifiers;
- authority conflicts and missing decisions;
- the smallest recommended next changes;
- audit scope and evidence limitations;
- explicit confirmation that no mutations were made.

Recommend `bootstrap-contract-governance` for structural governance changes and `contract-first-delivery-loop` for a specific tracked implementation task. Do not invoke either mutating workflow automatically.

## Stop Conditions

Stop or narrow the conclusion when:

- the repository or requested module cannot be accessed;
- active instructions prohibit the required inspection;
- a live external source is declared authoritative but cannot be read;
- evidence is too incomplete to distinguish a gap from an inaccessible source;
- the user requests a mutation that is outside this read-only audit.
