---
name: pr-review
description: Review GitHub pull requests independently using the current PR head SHA, live comments, code changes, checks, repository contracts, and code-graph context. Use when asked to review, re-review, inspect PR feedback, decide whether a PR is ready to merge, or submit a GitHub PR review.
---

# PR Review

Perform evidence-bound GitHub PR reviews. A review applies only to the exact current head SHA; prior comments, approvals, and green checks become historical evidence after a new commit.

## Review workflow

1. Read the live PR before drawing conclusions. Capture its state, base/head branches, exact `headRefOid`, linked issue, files, commits, reviews, issue comments, line comments, and check results. For GitHub repositories, use `gh` or GitHub-native APIs; do not infer this from the local branch.

   ```sh
   gh pr view <number> --repo <owner>/<repo> \
     --json state,baseRefName,headRefName,headRefOid,body,files,commits,reviews,comments,statusCheckRollup
   gh api --paginate repos/<owner>/<repo>/issues/<number>/comments
   gh api --paginate repos/<owner>/<repo>/pulls/<number>/reviews
   gh api --paginate repos/<owner>/<repo>/pulls/<number>/comments
   ```

2. Establish the review baseline. Check that each blocking historical finding is either fixed on the current head or remains open. Treat an approval, review, or CI result on any other SHA as stale. Record the reviewed SHA in the final result.

3. Read the repository's governing documents and the linked issue acceptance criteria before reviewing implementation. Verify contracts, APIs, policies, state transitions, persistence, security behavior, and operator documentation whenever the diff affects them. Do not request unrelated cleanup.

4. Inspect the changed code and its callers. If the repository has `.codegraph/`, use CodeGraph before `rg`, `find`, or broad source reads:

   ```sh
   codegraph explore "<changed symbol or review question>"
   codegraph node <symbol-or-file>
   ```

   Use the graph output to trace call paths, identify the blast radius, and select tests. If `.codegraph/` is absent, use targeted `rg` and small reads instead.

5. Verify the current head proportionately. Run the repository's documented gate and targeted regression tests for each credible finding. For CI, check that required checks are successful for the captured head SHA, not merely a branch-level status. Separate verified facts from unverified suggestions.

6. Report only actionable findings. Every blocking or warning finding must identify the changed file and line, explain a concrete failure path, name the impact, and propose a minimal correction. Do not report style-only preferences covered by formatters, hypothetical issues without a reachable path, or defects unrelated to the PR.

## Verdicts and re-review

Use `REQUEST_CHANGES` for correctness, security, data-loss, contract, or required-test failures. Use `APPROVE` only when no blocking issue remains on the reviewed SHA, required gates are satisfied, and GitHub allows this reviewer to approve the PR. Use `COMMENT` for non-blocking suggestions and for approval-equivalent single-maintainer reviews that cannot be submitted as formal approvals. Use `BLOCKED` when essential evidence is unavailable, such as missing PR access, unavailable required checks, inability to inspect the current head, or missing credentials for a required verification step. If evidence is incomplete, say what could not be verified; do not approve by default.

On re-review, repeat the live-state collection and rebind the result to the new current head SHA. Explicitly close or retain every prior blocking finding. A historical approval never approves a later commit.

## Publishing decision

Publish the GitHub review by default after completing the evidence-bound review. Do not publish only when the user explicitly asks for a chat-only review, says not to submit, or the PR cannot be written because of missing permissions, missing credentials, or a GitHub/API failure. When not publishing, return the full review in chat and include the closeout fields below with `GitHub Review Event: not_published`.

Before publishing, compare the authenticated reviewer with the PR author. GitHub does not allow PR authors to approve their own pull requests. For a same-author review, choose the final publishable event up front:

- Do not attempt `APPROVE` and do not rely on a rejected approval as control flow.
- If the evidence supports approval, publish `COMMENT` with the complete verdict and explicitly state that it is approval-equivalent but cannot be a formal GitHub approval because the reviewer is the PR author.
- If blocking issues exist, `REQUEST_CHANGES` is still allowed when policy and user intent require a formal review.
- For merge readiness, distinguish `review_result` from `github_approval_state`; a single-maintainer comment can record review evidence, but it does not satisfy a branch-protection rule requiring an approving review.

Publish `BLOCKED` verdicts as `COMMENT` unless the user explicitly asked not to submit or the write itself is blocked.

## Publishing a review

Bind every published review to the captured head SHA. Prefer the GitHub Review API because it accepts an explicit `commit_id`; `gh pr review` is acceptable only when exact commit binding is not required by the workflow.

Create a body file with this summary. Keep any inline comments narrowly scoped to changed lines and use the same footer.

```markdown
## PR Review

Verdict: <APPROVE|REQUEST_CHANGES|COMMENT|BLOCKED>
Reviewed Head SHA: `<sha>`
GitHub Review Event: <APPROVE|REQUEST_CHANGES|COMMENT|not_published>

## Findings

- [<severity>] `<file>:<line>` — <failure path, impact, and minimal correction>

## Verification

- `<command>` — <result>

## Residual Risk

- <risk or None>

---
Reviewer: <reviewer identity> · Model: <model or unknown>

<!-- pr-review-skill:v1
pr: <pr_number>
verdict: <verdict>
head_sha: <sha>
github_event: <APPROVE|REQUEST_CHANGES|COMMENT|not_published>
-->
```

The footer is a skill-level review artifact, not a project-specific agent role declaration. It must identify the actual reviewer identity and current model; use `unknown` rather than guessing.

Submit the review with the API when publishing. Set `event` to the final publishable event; for same-author approval-equivalent reviews, this must be `COMMENT`.

```sh
gh api repos/<owner>/<repo>/pulls/<pr_number>/reviews \
  -X POST \
  -f commit_id="<captured_head_sha>" \
  -f event="<APPROVE|REQUEST_CHANGES|COMMENT>" \
  -F body=@/tmp/pr-review.md
```

For same-author approval-equivalent reviews, use this final command shape:

```sh
gh api repos/<owner>/<repo>/pulls/<pr_number>/reviews \
  -X POST \
  -f commit_id="<captured_head_sha>" \
  -f event="COMMENT" \
  -F body=@/tmp/pr-review.md
```

Use `COMMENT` for `BLOCKED` closeout or same-author approval-equivalent reviews. In same-author approval-equivalent reviews, the final command must use `event="COMMENT"` directly and the body must state the GitHub approval limitation; never fabricate an approval.

## Closeout

State the PR number, verdict, reviewed SHA, executed verification, and any residual risk. Do not merge, alter code, or resolve conversations unless explicitly authorized by the user or the orchestrator's policy-controlled workflow.
