# Contract And Compatibility Reference

Load this reference only for shared, published, generated, schema, state, or consumer-visible contract changes.

## Resolve The Canonical Artifact

Record the following for each affected contract:

```text
Contract:
Provider or owner:
Known consumers:
Canonical artifact:
Generated outputs:
Compatibility policy:
Required gate:
```

Prefer an existing declared source of truth. Do not introduce a new contract format merely because one appears in this reference.

## Contract Maturity

Use maturity to select evidence, not to force a migration:

1. Narrative: prose describes intended behavior.
2. Structured: a schema or interface definition is machine-readable.
3. Executable: tests verify implementation against the contract.
4. Governed: compatibility and ownership checks can block integration.
5. Observed: runtime evidence can detect divergence after delivery.

Close the current task at the level required by the project. Record a maturity gap as follow-up instead of expanding the task automatically.

## Typical Artifacts And Gates

| Surface | Possible canonical artifact | Useful gate when already supported |
| --- | --- | --- |
| HTTP API | OpenAPI or framework schema | schema validation, breaking diff, implementation tests, generated-client drift |
| Event or message | AsyncAPI, JSON Schema, Avro, Proto | schema compatibility, producer/consumer tests |
| Protobuf or gRPC | `.proto` | lint and breaking-change detection |
| Consumer/provider interaction | consumer contract | consumer test and provider verification |
| CLI | command schema, help snapshot, golden JSON | arguments, exit codes, stdout/stderr, output compatibility |
| Database or stored data | migration plus schema/model | migration rehearsal and old/new version compatibility |
| Internal interface | typed interface plus tests | caller analysis and focused integration tests |
| State vocabulary | state model or enum schema | transition, retry, concurrency, and historical-data tests |

## Compatibility Dimensions

State which dimensions matter:

- Direction: backward, forward, or full compatibility.
- Representation: wire, serialization, source, generated-code, or storage compatibility.
- Semantics: defaults, ordering, error meaning, state transitions, permissions, and side effects.
- Time: immediate cutover, deprecation window, dual-read/write period, or versioned coexistence.

Do not assume an additive change is safe. New fields, enum values, output lines, defaults, or accepted states can break strict or exhaustive consumers.

## Change Decisions

- Preserve accepted contract behavior when fixing implementation drift.
- Update the canonical artifact and dependent tests together for intentional compatible changes.
- Require an explicit version or migration path for incompatible published changes.
- Keep a vertical slice together when contract, provider, consumer usage, and tests are required to demonstrate one coherent behavior.
- Split migrations or consumer rollouts only when the intermediate repository and deployed versions remain valid.
