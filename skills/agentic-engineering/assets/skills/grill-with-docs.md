---
name: grill-with-docs
description: Interview the user in rounds to sharpen a plan, bug, or design until there is shared understanding, writing GLOSSARY.md terms and docs/adr/ decisions as they settle. Use before /to-spec when scope, a domain rule, defect vs. trade-off, or proof is unclear, or when the user says "grill".
---

<!-- Adapted from mattpocock/skills (grilling + domain-modeling), MIT License, Copyright (c) 2026 Matt Pocock -->

# Grill With Docs

Interview the user until you both understand the change the same way. Do not plan the implementation or edit product code.

Read `AGENTS.md`, `ARCHITECTURE.md`, `GLOSSARY.md` and the ADRs in `docs/adr/` that touch the area. {{repo: domain reference docs to read, or delete this line}}

## Rounds

Map the work as a **design tree**: each decision branches into the decisions that depend on it. The **frontier** is every decision whose prerequisites are already settled. Ask the whole frontier in one round, then wait:

```
❓ **Q1** - **<title>**: <question, with options and the repo evidence>

➡️ <recommended answer>
```

- Word each question so that answering "yes" accepts your recommendation.
- If a question depends on another question still open in the same round, move it to a later round.
- **Facts are your job; decisions are the user's.** Never ask something the repo, the docs, or a read-only query can answer. Send a fresh subagent to look it up. Only the questions that depend on that fact wait for it; ask the rest now.
- Defect vs. trade-off: before treating an anomaly as a bug, check `Inspect` output and the domain docs. Some "wrong" results are deliberate.
- Stop when the frontier is empty and the user confirms you share an understanding. Then end with three short lists in the conversation: `Decisions`, `Out of scope`, `Open blockers`. `/to-spec` turns those lists into the spec.

## Domain language: `GLOSSARY.md`

- If the user uses a term that conflicts with `GLOSSARY.md`, say so immediately. Example: "The glossary says *X* means A, but you seem to mean B."
- If the user uses a vague or overloaded term, propose the precise one. Example: "account": the Customer or the User?
- Test boundaries with concrete edge-case scenarios from the domain.
- If the user says something the code contradicts, point out the contradiction.
- When a term is settled, add it to the root `GLOSSARY.md` straight away, creating the file if needed. Domain terms only, with no implementation details:

```md
**Order**:
A customer's request to buy one or more products.
_Avoid_: purchase, transaction
```

## Decisions: `docs/adr/NNNN-slug.md`

Offer an ADR only when the decision is **hard to reverse**, **surprising without context**, and **a real trade-off**. Skip it if any of the three is missing. To number it, take the highest existing number and add one. Format: a title plus 1–3 sentences covering the context, the decision, and why. Add `## Considered options` or `## Consequences` only when a future reader would need them. Feature status, progress, and proofs never go in an ADR.
