---
name: contract-first-dev-loop
description: >
  Use when Codex needs to run or install a transferable engineering method based on a contract-first, docs-driven development loop: confirm project plans and progress before editing, keep task scope small, analyze impact before shared changes, implement one verifiable slice, run meaningful verification, update progress tracking, and prepare or create a focused git commit. Trigger for phrases like "continue the development plan", "next tracked task", "make this project follow the report-workshop engineering methodology", "set up a docs-first delivery loop", or "formalize project development governance" in any software project.
---

# Contract-First Dev Loop

## Core Idea

Use a small governance stack to keep implementation work aligned with contracts:

1. Contract plan: requirements, API/interface contracts, module boundaries, error codes, permissions, state machines, and data/schema contracts.
2. Development rules: task granularity, change control, engineering standards, verification standards, and commit rules.
3. Progress tracking: milestone status, task list, contract checklist, test/acceptance log, and blockers.

Treat these documents as execution controls, not as after-the-fact summaries. Before editing, read the relevant controls. After verification, update the tracking files to match what actually happened.

For a ready-to-copy control-stack template and checklists, read `references/control-stack-template.md`.

## Project Structure Method

When applying this loop to an unfamiliar repo, first classify the project structure instead of assuming fixed paths.

Look for these layers:

- Agent guidance: `AGENTS.md`, `AGENT.md`, `CLAUDE.md`, `.codex/`, `.github/copilot-instructions.md`, or local equivalents.
- Product and module docs: root `README.md`, `docs/README.md`, module README files, technical solution files, decision records, or architecture docs.
- Contract docs: API plans, OpenAPI specs, CLI specs, internal interface docs, schemas, error codes, permission actions, task states, and data/result contracts.
- Development rules: roadmap, task granularity rules, engineering standards, change control, test and acceptance rules.
- Progress trackers: milestones, task list, contract checklist, test/acceptance log, blockers, release checklist.
- Runtime surfaces: backend, frontend, CLI, workers, migrations, deployment scripts, tests, fixtures, and generated clients.
- Local intelligence/tools: code graph, search index, API generator, schema generator, test runner, browser smoke tooling, or deployment scripts.

Map existing folders into three portable governance layers:

| Layer | Purpose | Common paths |
| --- | --- | --- |
| Contract layer | Defines stable interfaces and behavior | `docs/contracts`, `docs/api-design`, `docs/api`, `docs/10-*`, `openapi.*`, schemas, module technical docs |
| Development-plan layer | Defines execution rules and task order | `docs/development-plan`, `docs/11-*`, roadmap, engineering standards |
| Progress layer | Records current reality and next task | `docs/progress`, `docs/12-*`, task boards, test logs, blockers |

If the repo already uses different names, keep them. Do not rename the project to match the template unless the user asks for a governance migration.

If the project exposes an API, CLI, generated client, or agent-readable service contract, the contract layer should include an explicit API design chapter group rather than a single vague "API contracts" file. At minimum, cover unified protocol, query/read APIs, internal module interfaces, management/write APIs, CLI mapping, error codes and permission actions, and OpenAPI/schema generation.

## Task Cycle Control

Use the progress layer as the live queue, the development-plan layer as the execution rules, and the contract layer as the source of truth for behavior.

Default cycle:

1. Orient: confirm repo root, branch, dirty files, agent instructions, active model suitability, and available code-intelligence tools.
2. Select: infer or confirm one task from the progress tracker; if the user says "continue", choose the next unfinished tracked task.
3. Bound: state the task id/name, design basis, expected change surface, out-of-scope items, contract classes touched, and verification target.
4. Analyze: for shared symbols, contracts, schemas, permissions, task states, cross-module behavior, or unfamiliar paths, run impact analysis or targeted `rg`.
5. Implement: change the smallest complete slice that satisfies the task acceptance criteria.
6. Verify: run focused tests plus any contract, migration, build, browser, smoke, or deployment checks required by the changed surface.
7. Reconcile: update progress, contract checklist, test log, blockers, and decision records so docs match the verified result.
8. Close: review diff scope, exclude local artifacts/secrets, commit if the project workflow requires it, and report exact verification and any residual gaps.

Do not mark work as done because code was written. A task is done only when implementation, verification, contracts, and progress tracking agree.

## Start-of-Task Loop

1. Confirm the repo root, current branch, and worktree state.
2. Read project agent instructions first, such as `AGENTS.md`, `AGENT.md`, `.codex/*`, or equivalent local guidance.
3. Read the current control stack:
   - contract or API plan documents,
   - development plan and engineering rules,
   - progress tracking files.
4. If the user says only "continue", infer the next unfinished task from the progress tracker.
5. State the task boundary in concrete terms:
   - task id or short task name,
   - files/modules expected to change,
   - files/modules intentionally out of scope,
   - contract layer entries expected to change,
   - progress tracker entries expected to change,
   - verification required before closeout.

Stop and ask only when the control stack conflicts on task scope, or when the next task cannot be inferred safely.

## Contract-First Scope Control

Keep one task to one independently verifiable goal. Split or defer work when it changes a different contract class.

Use these default contract classes:

- API/CLI contract: routes, parameters, response envelope, pagination, error shape, generated clients.
- Internal interface contract: service method inputs/outputs, domain errors, ownership boundaries.
- Data contract: database schema, generated tables, files, result shape, migrations.
- Task/state contract: status values, retry rules, locking, result commit semantics.
- Security contract: permissions, audit events, credential handling, sensitive output.

Before changing a contract, update the contract document or decision record first. For destructive or incompatible changes, require an explicit versioning or migration plan.

Task slices that usually deserve separation:

- database/schema migration,
- API or CLI response shape,
- internal service interface,
- state-machine or retry semantics,
- permission/audit model,
- generated client or OpenAPI contract,
- frontend route/page completion,
- deployment/runtime environment behavior.

## Impact Analysis

Run impact analysis before editing shared symbols, cross-module behavior, data models, state machines, or public contracts.

Preferred order:

1. Use the repo's configured code-intelligence tool if one exists, such as GitNexus, Sourcegraph, IDE call hierarchy, or a local dependency graph.
2. If no code-intelligence tool exists, use targeted search with `rg` for callers, routes, schema names, task states, error codes, and permission actions.
3. Report high-risk impact before editing:
   - many direct callers,
   - public API or CLI consumers,
   - database migration or data compatibility risk,
   - permission/audit changes,
   - state-machine changes.

Do not let tool output override the project documents or tests. Treat it as evidence for blast radius and task boundaries.

## Implementation Loop

1. Re-read only the specific contract/design sections needed for the task.
2. Implement the smallest complete slice that satisfies the task's acceptance criteria.
3. Match existing local patterns for response envelopes, error handling, migrations, tests, logging, permissions, and frontend controls.
4. Avoid adjacent refactors unless they are necessary for the task.
5. Keep generated artifacts intentional: regenerate OpenAPI clients, schemas, migrations, or build outputs only when they are part of the task.
6. If implementation reveals a document/code mismatch, update the design or decision record before continuing with code that depends on the new interpretation.

## Verification

Use the repo's own verification baseline. If none exists, establish the narrowest meaningful set for the changed surface.

Minimum expectations:

- Logic change: focused unit tests plus existing related tests.
- API/CLI contract change: success, invalid input, permission failure, not found/unpublished state, and response-shape tests.
- Database/schema change: migration head check, generated SQL or migration dry run, and compatibility or rollback note.
- State-machine/task change: success, retry/failure, concurrency or locking where relevant, and "old data remains usable" behavior.
- Frontend route/page change: typecheck/build plus browser smoke for changed routes; auth redirects can count as success when the project defines that as the gate.
- Deployment/runtime change: health check, startup logs, env validation, and one user-visible route or API smoke.
- Milestone or runnable workflow closure: smoke or integration verification, not only unit tests.

Record exact commands and outcomes in the progress tracker when the project uses one.

## Closeout Loop

Before final response or commit:

1. Update progress tracking to reflect actual status, not intended status.
2. Update contract checklists for any API, CLI, internal interface, data, task, permission, or error-code change.
3. Update test/acceptance logs with commands run and notable gaps.
4. Record blockers instead of silently leaving partially verified work.
5. Check the diff for unrelated files, generated artifacts, local indexes, credentials, and formatting issues.
6. Create a focused git commit when the user's process requires commits.

If git or the filesystem blocks status/commit operations, leave the worktree untouched and report the exact blocker.

## Failure Shields

Preserve these safeguards when porting the method:

- If progress trackers are empty templates, initialize them with real live status before using them as the task queue.
- If multiple trackers conflict, prefer the most recent progress/blocker log for current state and use contracts for intended behavior.
- If a local code graph or index reports stale/multiple repos, refresh or specify the repo explicitly before trusting impact results.
- If verification tooling is unavailable, run the closest meaningful fallback and record the gap instead of silently marking the task done.
- If git is blocked by lock files, cloud-sync filesystem errors, or index corruption, report "implemented but not committed" and do not pretend closeout succeeded.

## Porting To A New Project

When installing this method in another repo:

1. Inventory the current structure and map it to the three governance layers:
   - `docs/contracts/` or `docs/10-api-design/`,
   - `docs/api-design/` when API/CLI/OpenAPI contracts are in scope,
   - `docs/development-plan/`,
   - `docs/progress/`.
2. Add the start/end loop to the repo's agent instructions.
3. Create the API/CLI contract chapter group before implementation when the product includes service endpoints, CLI commands, generated clients, or agent-facing API discovery.
4. Define task states, change levels, and contract classes.
5. Define the verification baseline for that tech stack.
6. Add ignore rules for local analysis outputs, generated indexes, caches, and secrets.
7. Seed progress tracking with current live status; do not leave only template tables.
8. Run the first real task end to end and tighten the templates based on friction.

Load `references/control-stack-template.md` when the user asks to set up the documents, migrate this method into a new repo, or review whether a project has enough governance to support agent-led implementation.
