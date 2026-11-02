# Governance Profiles

Select the lightest profile that resolves the repository's actual coordination risks. Tailor names and locations to existing conventions.

## Lite

Use by default for a small project or one primary team.

Required outcomes:

- active agent or contributor guidance points to the control loop;
- stable contracts have declared canonical artifacts or an explicit statement that no formal contract exists yet;
- one authoritative work tracker is named;
- completion criteria reference real validation commands;
- blockers and unresolved authority decisions have one visible location.

Do not create separate contract, plan, progress, and test-log directories unless existing complexity requires them.

## Standard

Use when multiple modules, generated consumers, shared interfaces, or several contributors create coordination risk.

Add only the relevant controls:

- contract owner and known consumers;
- compatibility direction and change policy;
- machine-readable schema or generation source when the project already uses one;
- automated lint, drift, or compatibility command;
- decision records for durable cross-module choices;
- review ownership for sensitive shared artifacts.

Do not add every control to every contract. Apply them to the surfaces that carry the risk.

## Extended

Use only when the user explicitly requests organization-wide, regulated, multi-repository, or externally administered governance.

Possible additions include approval workflows, central registries, policy-as-code, release controls, audit retention, or security-specific requirements. Treat external settings and organization policy as separate authorized work. Do not infer this profile from repository size alone.

## Profile Selection Questions

- How many independent providers and consumers must coordinate?
- Are contracts published or generated outside the module?
- Does a live work tracker already exist?
- Which failures currently escape review or CI?
- Are compatibility decisions reversible within one repository?
- Does the user actually request external, release, security, or compliance governance?
