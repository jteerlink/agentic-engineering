---
name: implement
description: Implement an approved .scratch spec or ticket test-first, run its proofs, get a fresh harness-verifier verdict, and log the result in the spec. Run as /implement <path-to-spec-or-ticket>, or with a small fix described in chat.
---

<!-- Adapted from mattpocock/skills (implement), MIT License, Copyright (c) 2026 Matt Pocock -->

# Implement

1. **Understand.** Read the spec or ticket, `AGENTS.md`, `ARCHITECTURE.md`, the relevant ADRs, and the code in the area. Set `Status: building`. Before editing, run the **Must not change** proofs (or the CI gate if there is no spec); if any is already red, stop and tell the user rather than building on a broken baseline. State a short plan and go. Stop for approval only at an approval gate listed in `AGENTS.md`.
2. **Red first.** Use `/tdd` at the agreed seams. Run each **Done when** proof and confirm it fails on an assertion. A missing test file or an import error does not count. If a test was written after the code, instead break the code on purpose, confirm the proof fails on an assertion, restore it, and log the break. If a proof already passes, it cannot show the change, so stop and fix the spec with the user. Skip this step for behavior-preserving work.
3. **Green.** Make the smallest change that satisfies Done when and the `AGENTS.md` Invariants. Never weaken, skip, or delete an existing assertion or fixture. Run single test files while you work. Once it's green, run every **Must not change** proof and the CI gate. Run proofs and the gate in the foreground: nothing wakes you when a background command finishes.
4. **Repair.** Fix root causes. After 3 failed repairs of the same proof or finding (counting verifier rounds too), stop and mark it blocked.
5. **Verify.** Spawn `harness-verifier` in the checkout that holds your changes (your worktree, if you are in one). Don't give it worktree isolation of its own, because a fresh worktree can't see uncommitted changes. Pass it the spec path. Repair any `Important` finding and run the verifier again. If you dispute a finding, ask the same verifier a follow-up with SendMessage (say why you think it's wrong, up to 3 rounds) instead of repairing blindly or spawning a new one.
6. **Log.** Append the verdict to the spec's `## Log`, with local and live results reported separately, and set `Status: done` or `blocked`. If blocked, record the root cause found (or best hypothesis), the approach taken, each fix tried and how it failed, and what remains untried, so the next session can resume from the spec. If a decision qualifies for an ADR or a term emerged, write it now (see `/grill-with-docs`).
7. **Hand back.** Draft a PR description: Problem, Change, Evidence (each proof command and its result, Local vs Live), affected records or users, and Reversibility (one-way or two-way door). If this work needed 2+ repairs for the same mistake in the repo, propose a one-line `AGENTS.md` Invariant or a check (`/retro`). Commit, push, or open a PR only when the user asks.
