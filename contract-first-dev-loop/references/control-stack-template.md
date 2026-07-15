# Contract-First Control Stack Template

Use this reference when creating, reviewing, or porting the development methodology into another project.

## 1. Structure Inventory

Before creating new documents, inventory the existing repo and map what is already present.

```text
repo-root/
+-- AGENTS.md or AGENT.md        # agent instructions and task loop
+-- README.md                    # product or developer entrypoint
+-- docs/                        # requirements, contracts, plans, progress
+-- backend/ or src/             # API, services, workers, jobs
+-- frontend/                    # UI routes, generated clients, browser tests
+-- cli/                         # commands and JSON output contracts
+-- migrations/                  # database migrations
+-- tests/                       # unit, API, integration, smoke
+-- deploy/ or infra/            # runtime env, compose, k8s, release scripts
+-- scripts/                     # repeatable maintenance or verification commands
+-- generated/                   # generated clients/schemas when intentionally tracked
```

Classify each discovered file into one of four roles:

- Product/module truth: requirements, user workflows, module boundaries, technical solutions.
- Contract truth: API, CLI, internal interfaces, schemas, state values, permissions, errors, audit events.
- Execution rules: roadmap, task granularity, change control, testing, commit and release rules.
- Live status: milestones, tasks, test results, blockers, release readiness.

Prefer adapting to the repo's existing names over forcing this template's names.

## 2. Suggested Directory Layout

```text
docs/
+-- contracts/
|   +-- README.md
|   +-- data-contracts.md
|   +-- task-state-contracts.md
|   +-- security-and-audit-contracts.md
+-- api-design/
|   +-- README.md
|   +-- 01-unified-protocol.md
|   +-- 02-query-apis.md
|   +-- 03-internal-module-interfaces.md
|   +-- 04-management-apis.md
|   +-- 05-cli-commands.md
|   +-- 06-error-codes-and-permission-actions.md
|   +-- 07-openapi-generation.md
+-- development-plan/
|   +-- README.md
|   +-- roadmap.md
|   +-- task-granularity.md
|   +-- engineering-standards.md
|   +-- change-control.md
|   +-- verification-and-acceptance.md
|   +-- contract-governance.md
+-- progress/
    +-- README.md
    +-- milestones.md
    +-- tasks.md
    +-- contract-checklist.md
    +-- test-acceptance-log.md
    +-- blockers.md
```

Use different names if the project already has a convention. Keep the three layers separate:

- Contract layer defines what must stay stable.
- Development-plan layer defines how work is executed.
- Progress layer records current reality.

If the project has APIs, CLIs, generated clients, or agent-facing service discovery, keep `api-design/` as a first-class contract chapter group. Do not collapse it into a single `api-contracts.md` file unless the project is very small and has no meaningful API surface.

## 3. Report-Workshop Pattern As A Portable Example

The source project that shaped this skill uses this mapping:

```text
docs/需求说明.md                 -> product/module entrypoint
docs/00-09*/README.md           -> module requirements and technical plans
docs/10-API设计计划/             -> contract layer
docs/11-开发计划与规范/          -> development-plan layer
docs/12-开发进度跟踪/            -> progress layer
docs/13-发布准备与部署联调/      -> release/deployment acceptance
docs/14-前端页面设计/            -> frontend page and UI contract
AGENT.md                        -> task start/end loop and code-intelligence rules
```

The transferable idea is not the numbering. The transferable idea is that one layer defines contracts, one layer defines execution rules, and one layer records current status.

The API design chapter group should remain visible in the generated project structure because it gates backend, frontend, CLI, SDK, and agent-facing integration work.

## 4. API/CLI Design Chapter Group

Create this chapter group when the project exposes HTTP APIs, RPC endpoints, CLI commands, generated clients, or OpenAPI/Swagger-style discovery.

Minimum files:

| File | Purpose |
| --- | --- |
| `README.md` | API design goals, principles, phase order, priorities, and non-goals. |
| `01-unified-protocol.md` | Request/response envelope, pagination, time format, IDs, versioning, errors, and compatibility rules. |
| `02-query-apis.md` | Read/query endpoints, filters, sorting, pagination, response fields, empty states, and published/unpublished access rules. |
| `03-internal-module-interfaces.md` | Service-to-service contracts, provider/consumer ownership, inputs/outputs, domain errors, idempotency, and transaction boundaries. |
| `04-management-apis.md` | Create/update/delete/publish/trigger operations, validation hooks, impact checks, concurrency, and audit requirements. |
| `05-cli-commands.md` | CLI-to-API mapping, parameters, JSON output shape, auth/env handling, exit codes, and scripting guarantees. |
| `06-error-codes-and-permission-actions.md` | Shared error code registry, permission action registry, audit events, and module ownership. |
| `07-openapi-generation.md` | OpenAPI/schema generation source, generated client policy, frontend/SDK/agent consumption, and regeneration tests. |

Recommended API design order:

1. Unified protocol.
2. Query/read APIs.
3. Internal module interfaces.
4. Management/write APIs.
5. CLI command mapping.
6. Error codes, permission actions, and audit events.
7. OpenAPI/schema generation and generated-client checks.

Each API or CLI design entry should state:

- name and owning module,
- method/path or command syntax,
- permission action and audit event,
- request parameters and validation,
- success response or JSON output,
- failure responses and error codes,
- idempotency, concurrency, and compatibility rules,
- provider/consumer dependencies,
- generated schema/client impact,
- required tests.

## 5. Agent Instruction Snippet

Add a project-specific version of this snippet to `AGENTS.md`, `AGENT.md`, or the repo's equivalent instruction file:

```markdown
## Project Control Loop

- At task start, read the current progress tracker, development rules, and relevant contract/design docs before editing, including the API/CLI design chapter group when endpoints, commands, generated clients, or OpenAPI contracts are touched.
- When the user says "continue", infer the next unfinished task from `docs/progress/tasks.md`.
- Keep the task boundary to one independently verifiable slice.
- Before editing shared symbols, public contracts, data schemas, state machines, permissions, or cross-module behavior, run impact analysis with the project's configured code-intelligence tool. If none exists, use targeted `rg` searches for callers and contract references.
- If implementation needs to change a contract, update the contract document or decision record before depending on the new behavior in code.
- At task end, run the required verification, update progress tracking with actual results, and create a focused git commit when requested by the project workflow.
```

## 6. Development-Plan README Outline

```markdown
# Development Plan And Standards

## Scope

List the parts of the product covered by the first implementation phase.

## Document Priority

1. Product requirements or module README files.
2. Technical solution documents.
3. API/CLI/interface contract plan.
4. Development plan and engineering standards.
5. Decision records created during implementation.

If implementation conflicts with documents, update the design or decision record before changing code.

## Principles

- Module boundaries first.
- Contract stability first.
- Small, independently verifiable tasks.
- Impact analysis before cross-module or shared changes.
- Query/read surfaces before management/write surfaces when that reduces integration risk.
- Compatibility protection for published APIs, CLI outputs, state values, stable codes, and result schemas.
- Observability, permission checks, and audit hooks as part of mainline work, not cleanup.

## Task Start/End Flow

1. Read progress, development rules, and relevant contract/design docs.
2. Identify the task boundary and expected verification.
3. Run impact analysis for shared or non-trivial changes.
4. Implement the smallest complete slice.
5. Run verification.
6. Update progress tracking.
7. Commit the focused change if the workflow requires it.
```

## 7. Task Template

```text
ID:
Milestone:
Module:
Task name:
Design basis:
Change scope:
Out of scope:
Inputs:
Outputs:
Permission actions:
Error codes:
Audit requirements:
Verification requirements:
Acceptance criteria:
Impacted contracts:
Rollback or compatibility plan:
Status:
Updated at:
```

## 8. Task States

Use a small shared state vocabulary:

| State | Meaning |
| --- | --- |
| `Not started` | No design or implementation work has begun. |
| `Designing` | Interface, data model, or implementation plan is being refined. |
| `In progress` | Code or docs are being changed. |
| `Self-testing` | Implementation is complete and local tests are running. |
| `Needs integration` | Module is ready and waiting for cross-module verification. |
| `Needs acceptance` | Integration is complete and awaiting acceptance criteria. |
| `Done` | Verification, docs, and tracking are complete. |
| `Blocked` | Work cannot continue due to an unresolved dependency, defect, or decision. |

Translate labels to the project's language, but keep the meanings stable.

## 9. Change Levels

| Level | Type | Required handling |
| --- | --- | --- |
| L1 | Module-internal change | Module tests are usually enough. |
| L2 | Contract change | Update contract docs before implementation. |
| L3 | Data/schema change | Add migration, impact analysis, compatibility or rollback note. |
| L4 | Behavior/state/security semantic change | Add decision record and regression tests. |
| L5 | Breaking change to published behavior | Default to not allowed; require versioning or migration period. |

Upgrade a task to the higher level when a local change affects public contracts, state values, permissions, audit, result schemas, or downstream consumers.

## 10. Contract Checklist

Track each contract with these fields:

```text
Contract id:
Type: API | CLI | Internal interface | Data | Task/state | Permission/audit
Provider:
Consumers:
Inputs:
Outputs:
Errors:
Permissions:
Audit events:
Idempotency:
Compatibility rule:
Verification:
Status:
Last changed:
```

Freeze contracts once integration starts. After freeze, allow additive compatible changes only unless a decision record approves a versioned breaking change.

## 11. Verification Baseline

Define commands per stack. Example categories:

| Change surface | Required verification |
| --- | --- |
| Backend logic | Focused unit tests and relevant regression tests. |
| API/CLI | Success, invalid input, permission denied, not found, response shape, and generated schema/client checks. |
| Database | Migration head check, generated SQL or dry run, model tests, compatibility note. |
| Frontend | Typecheck, unit tests, build, and browser smoke for changed flows. |
| Async task/state machine | Success path, retry/failure path, concurrency/locking, old data remains usable. |
| Milestone closure | End-to-end or smoke verification that exercises the runnable user flow. |

Record commands and outcomes in `docs/progress/test-acceptance-log.md`.

## 12. Task Cycle Checklist

Use this checklist for every tracked implementation slice:

```text
Start:
[ ] Repo root, branch, dirty files checked.
[ ] Agent instructions and local workflow rules read.
[ ] Progress tracker read; one task selected.
[ ] Relevant contract/design docs read.
[ ] Task boundary and out-of-scope items stated.
[ ] Impact analysis done when shared contracts/symbols/schemas/states are touched.

Build:
[ ] Smallest complete slice implemented.
[ ] Existing local patterns followed.
[ ] Generated artifacts updated only when required.
[ ] Contract or decision docs updated before relying on changed behavior.

Verify:
[ ] Focused tests run.
[ ] Contract/schema/migration/build/browser/smoke checks run when applicable.
[ ] Verification gaps recorded if a tool is unavailable.

Close:
[ ] Progress/task status updated.
[ ] Contract checklist updated.
[ ] Test/acceptance log updated.
[ ] Blockers recorded or cleared.
[ ] Diff reviewed for scope, secrets, caches, indexes, and unrelated files.
[ ] Focused commit created when the project requires it.
```

## 13. Progress Tracker Rules

- Update `tasks.md` when a task starts, changes state, or finishes.
- Update `contract-checklist.md` when any contract is designed, implemented, frozen, or changed.
- Update `test-acceptance-log.md` after every meaningful verification run.
- Update `milestones.md` only when all required tasks and acceptance checks for that milestone are complete.
- Update `blockers.md` immediately when work cannot safely continue.

Never mark a task done just because code was written. It is done only when implementation, verification, documents, and tracking agree.

## 14. Commit Hygiene

Before committing:

- Review changed files for task scope.
- Exclude local indexes, caches, secrets, generated analysis folders, and unrelated metadata.
- Run the project's formatting or diff check.
- Use a commit message that names the task id or contract changed.
- If code structure or call relationships changed and the repo uses a code graph, refresh the index after commit.
