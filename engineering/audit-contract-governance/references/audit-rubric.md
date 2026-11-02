# Contract Governance Audit Rubric

Use this rubric to organize evidence, not to manufacture a numeric score.

## 1. Authority

Check whether contributors can identify:

- active instructions for the current path;
- canonical contract sources;
- authoritative work status;
- decision ownership when sources conflict.

Strong evidence names authorities and precedence. Weak evidence relies on filenames, timestamps, or tribal knowledge.

## 2. Contract Coverage

Check whether actual stable surfaces are represented:

- public or shared APIs and CLIs;
- internal interfaces with multiple consumers;
- schemas and persisted data;
- stable state values, errors, or generated outputs.

Do not require irrelevant contract types.

## 3. Executability

Classify representative contracts:

1. Narrative: prose only.
2. Structured: machine-readable schema or interface.
3. Executable: implementation is tested against it.
4. Governed: ownership or compatibility gates can block integration.

Higher maturity is useful only where the coordination risk justifies it.

## 4. Compatibility

Check whether changes consider:

- provider and known consumers;
- backward, forward, wire, source, storage, or behavioral compatibility;
- deprecation or migration when breaking behavior is allowed;
- generated clients and strict or exhaustive consumers.

## 5. Delivery Loop

Check whether one task can be:

- selected from one authoritative queue;
- bounded as an independently verifiable outcome;
- traced to design or contract intent;
- verified with real commands or gates;
- closed without duplicating volatile status.

## 6. Verification

Check whether required evidence is proportional to the changed surface and whether documented checks are executable, automated, or consistently recorded.

Do not require release, security, deployment, or runtime controls unless they are in the audit scope or part of an accepted contract being evaluated.

## Severity Guidance

- P0: Governance directs unsafe or materially destructive behavior with no effective stop or authority check.
- P1: A likely contract, compatibility, or status conflict can cause incorrect delivery across consumers or modules.
- P2: A missing or manual control creates recurring drift or weak verification but has a practical workaround.
- P3: A clarity, organization, or efficiency improvement with limited immediate delivery risk.

State uncertainty when evidence is incomplete. Do not inflate severity to make the report appear comprehensive.
