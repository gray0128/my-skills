---
name: bootstrap-contract-governance
description: >
  Use when the user explicitly invokes this skill to install, migrate, or formalize a minimal contract-governance system in a software repository. Inventory existing instructions, contracts, trackers, tests, and CI; declare authoritative sources; choose the lightest suitable governance profile; add only missing controls; seed them with real project state; and verify the resulting links and configuration. Do not implement product features, execute the next tracked task, perform a read-only audit only, or introduce release, security, and runtime programs unless the user explicitly includes them.
---

# Bootstrap Contract Governance

## Goal

Install the smallest governance control surface that makes contracts, delivery rules, verification, and current work status discoverable and internally consistent.

Adapt to the repository. Do not reproduce a preferred directory tree, rename existing artifacts, or create duplicate sources of truth merely to match a template.

## Precedence And Authorization

Apply current user instructions first, then active repository guidance such as `AGENTS.md`, then established project conventions, then this skill's defaults.

Treat this skill as authorization to change local governance artifacts required by the request. Do not implement product behavior, rewrite application architecture, create external issues or PRs, change branch protection, or deploy anything unless separately authorized.

## Establish The Bootstrap Contract

Resolve and, when useful, state briefly:

```text
Governance outcome:
Repository scope:
Existing authorities to preserve:
Missing controls to add:
Selected profile:
Files or configuration in scope:
Out of scope:
Validation:
Stop conditions:
```

## Inventory Before Designing

Inspect only enough to map:

- active agent and contributor instructions;
- product and module documentation;
- machine-readable and narrative contracts;
- existing Issue, task, PR, CI, milestone, or Markdown tracking;
- test, schema, generation, and compatibility commands;
- code ownership and decision records when present;
- local code-intelligence and repository tools.

Use the project's configured discovery tools and respect repository-specific routing. Prefer declared authorities over guessed conventions. If several artifacts conflict, classify the conflict before adding new controls.

## Choose The Lightest Profile

Load `references/governance-profiles.md` to select and tailor a profile.

Default to the Lite profile. Use a stronger profile only when repository evidence or the user's stated needs justify more ownership, compatibility, or cross-team coordination controls.

Do not infer that a public API, deployment stack, or security program exists. Add controls only for actual project surfaces.

## Design Around Authorities, Not Folders

The installed system should make five answers easy to find:

1. Which instructions govern work here?
2. Which artifact defines each stable contract?
3. Which system records current work state?
4. Which checks establish completion for each relevant change surface?
5. Which unresolved conflict or decision blocks safe delivery?

Use `references/artifact-patterns.md` for compact adaptable patterns. Reuse existing files when they already answer these questions. Add an index or pointer instead of copying volatile state.

## Prevent Duplicate Truth

- Keep live Issue or task systems authoritative when the project already uses them.
- Keep CI authoritative for individual run results; store links or command names rather than copied logs.
- Keep machine-readable schemas authoritative for interface shape only when the project declares them canonical.
- Keep decision records for durable choices, not routine task state.
- Keep progress Markdown as an index unless the project explicitly makes it the live tracker.
- Do not choose an authority solely because it is newer.

When authority cannot be resolved safely, record the decision needed and stop before creating another competing source.

## Implement The Governance Slice

Create or update only the minimum coherent set of controls. Typical outcomes may include:

- a concise project-control section in active agent guidance;
- a source-of-truth or contract registry;
- a task selection and completion rule;
- a verification map using real project commands;
- a pointer to the authoritative tracker and blockers;
- an ignore rule for local analysis outputs when needed.

Seed new controls with observed project state. Do not leave placeholder-only tables that could be mistaken for live governance.

Add automated gates only when the repository already has the relevant tooling and the requested scope authorizes configuration changes. Otherwise document the validated command or record the missing capability as a follow-up.

Keep release, security, deployment, and runtime controls out of the default bootstrap. Include them only when explicitly requested or already required by the repository's accepted delivery contract.

## Verify The Installed Controls

Check proportionately:

- instruction and documentation links resolve;
- named authoritative artifacts exist;
- configuration and structured files parse;
- documented commands exist and are plausible for this repository;
- no new tracker duplicates an established live source;
- no placeholders, unrelated files, or local artifacts remain;
- the resulting control loop can identify one real next task or explicitly explain why it cannot.

Validate governance artifacts, links, and structured configuration directly. Do not run product tests merely to prove that a documented command exists. Run product tests only when the bootstrap changes executable CI or test configuration that requires integration validation, or when the user explicitly requests them.

## Closeout

Report:

- the installed governance profile;
- authorities preserved and controls added;
- exact files or configuration changed;
- validation performed;
- decisions or capabilities still missing;
- confirmation that product implementation was not started.

## Stop Conditions

Stop and request the smallest missing decision when:

- competing artifacts claim the same authority with materially different content;
- selecting a work tracker or canonical contract requires organizational ownership not present in the repository;
- the requested profile requires external administration or writes not authorized by the user;
- unrelated user changes overlap the governance files that must change;
- completing the bootstrap would require product implementation or a materially broader migration.
