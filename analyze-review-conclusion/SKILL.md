---
name: analyze-review-conclusion
description: Analyze review conclusions, audit reports, PR review summaries, architecture review feedback, or evaluation findings against the project's real progress, implementation state, accepted plans, Issues/PRs, docs, contracts, and verification evidence. Use when Codex is asked to judge whether review findings should be adopted now, treated as already planned later work, partially accepted, rejected as stale or unsupported, or escalated for human decision, and to generate a Markdown report named 评审报告分析采纳结论.md.
---

# Analyze Review Conclusion

Use this skill to turn review conclusions into a careful adoption decision. Do not treat the review text as automatically correct; verify each finding against the project's current source of truth before recommending action.

## Workflow

1. Resolve the target review artifact and the expected report location. If the user does not specify a location, write `评审报告分析采纳结论.md` next to the review artifact; if there is no artifact file, write it at the repository root.
2. Read project instructions first, especially `AGENTS.md`, workflow skills, and any repo-specific source-of-truth guidance.
3. Collect current truth sources:
   - Review conclusion, audit report, review comments, or evaluation findings being analyzed.
   - Current plan or roadmap documents, active Issues/PRs, milestones, release notes, and recent human decisions.
   - Relevant implementation, contracts, schemas, tests, docs, CI status, and existing verification evidence.
   - For CNB repositories, use `cnb` CLI for live Issue/PR/check state.
   - If a `.codegraph/` directory exists and code understanding is needed, use CodeGraph before grep/find/manual reading.
   - For UI/UX validation, prefer Chrome-based verification when available.
4. Normalize review content into distinct items. Assign each item an ID, claim, affected area, cited evidence, implied action, and severity or business impact when available.
5. Verify each item against real state:
   - Is the premise true in current code/docs/contracts/live Issue or PR state?
   - Is the issue already fixed, explicitly planned, intentionally out of scope, or still unaddressed?
   - Does adoption fit the current phase goal, accepted architecture boundary, and planned delivery sequence?
   - Would adoption introduce scope creep, contradict a later human decision, or require new product/design approval?
6. Classify each item with exactly one decision:
   - `采纳-立即处理`: valid, in current scope, and should become near-term work.
   - `采纳-纳入后续计划`: valid but belongs to an existing or newly proposed later phase.
   - `部分采纳`: core concern is valid but the proposed fix is too broad, risky, or mismatched.
   - `不采纳`: stale, already superseded, unsupported by evidence, contradicts accepted decisions, or outside project boundary.
   - `已解决`: real issue existed but current code/docs/plan already addresses it.
   - `需人工决策`: valid tradeoff or scope/architecture/product decision cannot be settled from project evidence alone.
7. Generate `评审报告分析采纳结论.md` from `assets/report-template.md`. Replace placeholders with concrete evidence and leave no unfinished marker text.
8. Run `python3 skills/analyze-review-conclusion/scripts/validate_report.py <path/to/评审报告分析采纳结论.md>` and fix any reported structural gaps.

## Decision Rules

- Prefer current live state and latest explicit human decisions over older plans, stale review comments, or memory.
- Do not mark a finding as `采纳-纳入后续计划` unless a concrete plan, Issue, milestone, roadmap entry, or proposed follow-up action is cited.
- Do not reject a finding only because it is inconvenient; reject only with evidence.
- Do not silently convert broad review suggestions into implementation work. If the finding changes product scope, architecture boundary, security posture, or delivery phase, classify it as `需人工决策`.
- Separate "reviewer proposed solution" from "underlying problem." It is valid to reject the solution while partially adopting the problem statement.
- Keep action items traceable: every accepted item must map to an owner/source, target phase, Issue/PR/doc path, or explicit next step.

## Report Requirements

The report must be a standalone Markdown file named exactly `评审报告分析采纳结论.md`.

Include these sections:

1. `结论摘要`: counts by decision type and the overall recommendation.
2. `依据来源`: review artifacts and project truth sources checked, with paths, Issue/PR numbers, commands, or verification notes.
3. `逐项分析`: a table or repeated blocks containing item ID, review claim, verification evidence, decision, rationale, and action.
4. `采纳与处理计划`: immediate actions, planned-later actions, and items requiring human decision.
5. `风险与待确认事项`: residual uncertainty, missing evidence, and follow-up questions.

State uncertainty explicitly when evidence is incomplete. Do not imply that planned-later work is already delivered.
