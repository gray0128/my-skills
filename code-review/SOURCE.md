# Source

- Skill: `code-review` (`/code-review`)
- Collected from: [TaXue2025](https://x.com/TaXue2025/status/2100947197332517017) (2026-09-18)
- Origin: Cursor team kit skill `thermo-nuclear-code-quality-review`, later renamed and shipped as a Grok Build built-in skill (`crates/codegen/xai-grok-shell/skills/code-review/SKILL.md`). The current public `xai-org/grok-build` tree no longer vendors this file; this copy matches the widely mirrored built-in text (blob `2063a9c87c4d4e682a1173c4433a84143c02e5a4`).
- Related Cursor source: [cursor/plugins](https://github.com/cursor/plugins/blob/main/thermos/skills/thermo-nuclear-code-quality-review/SKILL.md)

This skill is a **maintainability / structure** review, not a GitHub/CNB PR-publishing workflow. Use `pr-review` or `cnb-pr-review` when the job is evidence-bound platform review submission.

## Recommended invocation overlay

From the source tweet, pair `/code-review` with a concrete target and this quality frame:

```text
/code-review 梳理一下这个 <TARGET> 的 skill，保持优雅的工程质量、良好的可维护性和极佳的用户体验。以重新定义问题为导向，运用第一性原理与MECE原则、量化思维，驱动开发与测试的系统性优化。
```

Replace `<TARGET>` with the skill, module, or diff under review.
