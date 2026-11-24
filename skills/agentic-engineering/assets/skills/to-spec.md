---
name: to-spec
description: Turn the current conversation into an ephemeral spec at .scratch/<slug>/spec.md (problem, decisions, done-when proofs, must-not-change, seams) for /implement. No interview; synthesize what was discussed. Skip for small fixes.
---

<!-- Adapted from mattpocock/skills (to-spec), MIT License, Copyright (c) 2026 Matt Pocock -->

# To Spec

Write down what was decided, without running a new interview. The spec is a working document: it is gitignored and deleted after merge. Anything that must outlive it goes in `GLOSSARY.md`, `docs/adr/`, tests, or the PR description.

## Steps

1. If you haven't already, read `AGENTS.md`, `ARCHITECTURE.md`, `GLOSSARY.md`, the relevant ADRs, and the source and tests in the area. Use the glossary's terms throughout.
2. **Agree the testing seams with the user first.** Prefer existing seams, ideally one, at the highest level that still catches the bug. {{repo: name the usual highest seam, e.g. a scenario/fixture test, and its prior-art file}} Give each seam one line on what it catches and what it misses.
3. Draft the spec below. Every **Done when** item needs a runnable proof command. At least one per item must fail on the current code, unless the work is behavior-preserving; say so under Done when if it is. Expected values come from an independent source: {{repo: the repo's source of truth, e.g. production actuals, a spec doc}}, or a worked example. Never recompute them the way the code does. {{repo: if the repo has recorded real data (e.g. a fixture of production actuals), add "If the change alters existing output, at least one Done-when proof must check against <that data>, not only literals."; otherwise delete this sentence}}
4. Show the user the spec and wait for approval. Revise on feedback.
5. Write `.scratch/<slug>/spec.md` with `Status: approved`. End by printing `/implement .scratch/<slug>/spec.md`.

## Template

```md
# <title>
Status: draft | approved | building | verifying | done | blocked

## Problem
<what the user sees today, in their words>

## Solution
<what they will see afterwards>

## Decisions
- <decision and why; link docs/adr/NNNN-*.md if one was written>

## Done when
- [ ] <observable behavior> — proof: `<command>` (fails today)

## Must not change
- [ ] Existing behavior stays the same — proof: `{{repo: regression suite command}}`
- [ ] <other behavior to protect> — proof: `<command>`

## Testing seams
- <seam>: catches <x>, misses <y>. Prior art: <similar test>

## Out of scope
- <explicit non-goals>

## Risks & gates
- <AGENTS.md invariants touched, approvals needed, live checks that need credentials or network>

## Log
<written by /implement: auditor verdict with local and live results; if blocked: root cause, approach, tried / failed / untried>
```

Keep paths and code out of Decisions and Solution, because they go stale. Paths belong only in proof commands and seams. If the spec has no Done-when items, it is not a spec yet.
