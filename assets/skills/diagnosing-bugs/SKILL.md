---
name: diagnosing-bugs
description: Diagnosis loop for wrong results, crashes, flaky behavior, or slow runs — build a tight red-capable loop before forming any hypothesis. Use when the user says "diagnose"/"debug this" or reports something broken, wrong, or slow.
---

<!-- Adapted from mattpocock/skills (diagnosing-bugs), MIT License, Copyright (c) 2026 Matt Pocock -->

# Diagnosing Bugs

Read `GLOSSARY.md` and the ADRs in the area. Redact secrets and tokens from everything you show. Show only the record key and the fields that carry the signal, never whole row dumps.

## 1. Build a feedback loop

This is the skill. Find **one command** that goes red on *this* symptom, and do not form hypotheses until you have it. Options, in order of preference:

1. A failing test at a seam that reaches the bug, often a new fixture scenario.
2. Offline replay of captured inputs: fast and deterministic. {{repo: prior-art replay test, or delete}}
3. A differential: the same input on two revisions or configs, diffing the outputs. Or `git bisect run` it.
4. The live system ({{repo: live run command}}). This is slow, so use it only to capture data for options 1–2.

Make the loop tighter, sharper (assert on the exact value, not just "didn't crash"), and deterministic. When you can't build one, say so, list what you tried, and ask for access, data, or permission. Don't guess.

**Done when** you have already run the command, shown its output, and it is red-capable, deterministic, fast, and runs without you.

## 2. Reproduce and minimise

Confirm it fails with the **user's** symptom, not a nearby one. Then cut inputs, fields, and steps one at a time until every remaining element is needed for the failure.

## 3. Hypothesise

Write 3–5 ranked, falsifiable hypotheses: "If X is the cause, changing Y makes it disappear." Show the list to the user before testing. They may know history or source quirks that reorder it. If they're away, continue with your own ranking.

Before calling it a defect, also consider whether this could be an intentional trade-off. If the fix crosses an `AGENTS.md` approval gate, propose it with the affected records first.

## 4. Instrument

Each probe tests one prediction, and you change one variable at a time. Tag every temporary log `[DEBUG-xxxx]` so a single grep removes them. For slow runs, profile first, then bisect.

## 5. Fix and regression test

Turn the minimised repro into a failing test at a seam that exercises the real call path. If the only seam is too shallow to reproduce the bug, record that as a finding. Watch the test fail, fix the code, watch it pass, then rerun the original loop. Then spawn `harness-verifier` on the diff (with no spec it reports the Standards axis only) and repair any `Important` finding. If the fix is too big for that (several files, a design choice, or an approval gate), stop after the failing test and go through `/to-spec` -> `/implement` instead.

## 6. Clean up

- The original loop is green.
- The regression test passes, or the missing seam is documented.
- `harness-verifier` returned PASS on the diff.
- `grep -rn "DEBUG-"` is empty.
- Throwaway scripts are deleted.
- The hypothesis that proved correct is written in the commit or PR message.
