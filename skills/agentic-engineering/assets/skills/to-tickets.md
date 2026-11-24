---
name: to-tickets
description: Split an approved .scratch spec into tracer-bullet tickets under .scratch/<slug>/issues/, each with blocking edges and acceptance proofs. Use only when the work will not fit one session.
---

<!-- Adapted from mattpocock/skills (to-tickets), MIT License, Copyright (c) 2026 Matt Pocock -->

# To Tickets

Split the spec into **vertical slices**. Each slice is a narrow but complete path that can be verified on its own (data → logic → interface → test) and fits one fresh context window. If a prefactor would make the change easy, do it first as its own ticket.

**Wide refactors** are the exception. If one mechanical change fans out across many call sites, sequence it **expand → migrate in batches → contract**. Each batch is a ticket blocked by the expand step, and the contract step is blocked by every batch.

## Steps

1. Read the spec (the argument, or `.scratch/*/spec.md` from this conversation) and the code it touches.
2. Present a numbered list. For each ticket give the **title**, **blocked by**, and **what it delivers**. Ask whether the granularity, the blocking edges, and the merges/splits are right. Iterate until the user approves.
3. Write one file per ticket at `.scratch/<slug>/issues/NN-<slug>.md`, numbered from `01` in dependency order:

```md
# NN: <title>
Blocked by: <NN, NN> | none
Status: ready | building | verifying | done | blocked

<the end-to-end behavior this ticket makes work>

## Done when
- [ ] <criterion> — proof: `<command>` (fails today)

## Must not change
- [ ] <copied from the parent spec's Must not change> — proof: `<command>`
```

Work the frontier: any ticket whose blockers are all `done`. Run `/implement .scratch/<slug>/issues/NN-<slug>.md` for each one.
