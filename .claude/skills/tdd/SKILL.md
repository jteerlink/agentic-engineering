---
name: tdd
description: Red-green test-first rules — test only at agreed seams, expected values from an independent source, one vertical slice at a time. Use when building features or fixing bugs test-first.
---

<!-- Adapted from mattpocock/skills (tdd), MIT License, Copyright (c) 2026 Matt Pocock -->

# TDD

Use `GLOSSARY.md` terms in test names, and respect the ADRs in the area.

## Good tests

- Test behavior through public interfaces, so a refactor that doesn't change behavior never breaks the test. The name says *what* happens: `test_expired_card_is_declined`, not `test_calls_card_validator`.
- **Seams:** test only at seams agreed with the user (in the spec, or asked before the first test). The usual seam is `tests/test_harness.py` (offline checks over the repo's files).
- **Mocks:** mock only at system boundaries, meaning the network, time, and randomness. Never mock our own modules. Unit tests stay offline (`AGENTS.md`).

## Anti-patterns

- **Implementation-coupled:** mocks internal collaborators, tests private helpers, or checks through a side channel. The giveaway is that a pure refactor breaks it.
- **Tautological:** the expected value is recomputed the way the code computes it, so the test can never disagree with the code. Expected amounts must come from an independent source:
  - `SKILL.md` and `references/guide.md`;
  - a worked example from a spec or domain doc;
  - a literal the user confirmed.
  `assert total(cart) == sum(i.price for i in cart)` is tautological; `assert total(cart) == Decimal("42.50")` is not.
- **Horizontal slicing:** writing all the tests first and then all the code. Work one slice at a time instead: one test, one minimal change, repeat.

## Loop

- Red before green. Write the failing test, watch it fail on an assertion, then write only enough code to pass it.
- One seam, one test, one change per cycle.
- Never refactor mid-cycle. Refactor only after green, as its own step, with the tests still passing.
