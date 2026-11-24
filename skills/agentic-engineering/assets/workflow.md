# Feature Workflow

```text
/grill-with-docs (if unclear) -> /to-spec -> /implement -> PR
                                        \-> /to-tickets -> /run-tickets -> draft PR  (multi-session work)
```

## Where things live

| What | Where | Lifetime |
|---|---|---|
| Domain terms | `GLOSSARY.md` (created on first term) | Durable |
| Hard-to-reverse decisions | `docs/adr/NNNN-slug.md` | Durable |
| Plan, proofs, progress | `.scratch/<slug>/spec.md` (+ `issues/NN-*.md`) | Ephemeral, gitignored; delete after merge |
| Proof of done | Tests in the repo + PR description evidence | Durable via git |

## Loop

1. **Clarify** (`/grill-with-docs`, only when scope, a domain rule, defect vs. trade-off, or proof is unclear): rounds of numbered questions with recommended answers; terms and ADRs written as they settle.
2. **Spec** (`/to-spec`; skip for small fixes): agree test seams, then Done-when items each with a proof that fails today, Must-not-change proofs, risks and approval gates. User approves before building.
3. **Tickets** (`/to-tickets`, only for multi-session work): vertical slices with blocking edges. `/run-tickets <spec>` works the frontier unattended: each ticket through `/implement` in one worktree, a commit per ticket, one draft PR per spec, stopping at the first blocked ticket. It never merges.
   Dashboard (optional, read-only, if `docs/harness/dashboard.html` is installed): `ln -sf ../docs/harness/dashboard.html .scratch/dashboard.html && python3 -m http.server 8765 --bind 127.0.0.1 -d .scratch`, then open http://127.0.0.1:8765/dashboard.html. It serves only `.scratch/`. `/run-tickets` starts it in the background and gives you the URL; outside a run, ask the agent to start the ticket board.
4. **Implement** (`/implement <spec>`): `/tdd` red-first at agreed seams, smallest change, 3-repair limit, fresh `harness-verifier` (Spec and Standards axes, Local vs Live proofs), result logged in the spec.
5. **PR**: evidence from the spec's Log; commit or open a PR only when asked.

Bugs: `/diagnosing-bugs` first (tight red loop before hypotheses). It fixes a small bug itself and runs `harness-verifier` on the diff; a bigger fix goes through `/to-spec` -> `/implement`.

## Phase boundaries

At the end of a phase, take the first that applies:

1. **Continue** if the next phase needs this one as a primary source (grilling -> spec -> implement is always continue) or there is room left.
2. **`/clear`** if nothing in the session matters for what comes next.
3. **`/handoff`** only if the work is travelling: another harness, directory, or person.
4. **Subagent** if the task can run unattended (review, fact-finding).
5. **`/compact <what's next>`** otherwise.

Never compact mid-phase. A blocked spec's Log (root cause, approach, tried / failed / untried) is the resume point.

Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT).
