---
name: agentic-engineering
description: Inspect a repository and create or reconcile its agent harness — AGENTS.md (with CLAUDE.md as @AGENTS.md), ARCHITECTURE.md, docs/harness/workflow.md, and Pocock-style skills (grill-with-docs, to-spec, to-tickets, implement, tdd, diagnosing-bugs, handoff, retro) plus run-tickets (unattended ticket runs into one draft PR), an auditor agent, and an optional read-only ticket dashboard (docs/harness/dashboard.html), mirrored for Claude Code and Codex. Plans are ephemeral .scratch specs; durable knowledge is GLOSSARY.md and docs/adr/.
---

<!-- Skills under assets/skills (except run-tickets, written here) are adapted from mattpocock/skills, MIT License, Copyright (c) 2026 Matt Pocock -->

# Agentic Engineering

Give coding agents short, accurate direction: a root guide (`AGENTS.md`), an architecture map (`ARCHITECTURE.md`), hard invariants, real commands, and a light loop (`/grill-with-docs` -> `/to-spec` -> `/implement` -> `auditor`). Reflect the target repository as it exists.

`<skill-dir>` means the directory containing this `SKILL.md`. Read [references/guide.md](references/guide.md) before writing anything.

## Install

1. Discover the target repository per `references/guide.md`: audit existing guides; collect invariants, commands, inspection tools, canonical patterns, the usual test seam, the independent source of truth for expected values, external services, and sensitive-data rules. Then ask the user whether to install the read-only ticket dashboard (`docs/harness/dashboard.html`, a live board of `/to-tickets` tickets served locally). If it is already installed, update it without asking.
2. Write or reconcile in the target repository:
   - `AGENTS.md` (canonical) and `CLAUDE.md` (`@AGENTS.md` plus Claude-only notes);
   - `ARCHITECTURE.md`;
   - `<skill-dir>/assets/workflow.md` -> `docs/harness/workflow.md` (link it from README if one exists);
   - each `<skill-dir>/assets/skills/<name>.md` -> `.claude/skills/<name>/SKILL.md`, then replace every `{{repo: ...}}` marker with the repo's real seam, command, or source of truth (or delete the line if it doesn't apply);
   - one mirror for Codex: `ln -s ../.claude/skills .agents/skills` (never two copies);
   - `<skill-dir>/assets/agents/auditor.md` -> `.claude/agents/auditor.md` (fill its markers); `<skill-dir>/assets/agents/auditor.toml` -> `.codex/agents/auditor.toml` (it only points to the `.md`);
   - only if the user said yes to the dashboard in step 1: `<skill-dir>/assets/dashboard.html` -> `docs/harness/dashboard.html` (copied as is; it has no markers);
   - append `.scratch/`, `.agents/` and `.claude/` to `.gitignore` (add each line only if missing).
3. If an architectural boundary already exists, seed `docs/adr/0001-<slug>.md` and an offline test that guards it. Don't create `GLOSSARY.md` up front; `/grill-with-docs` creates it on the first term.
4. **Migrating an older harness** (ledger flow): turn decisions recorded in `docs/features/*.json` into ADRs and grep-style proofs into tests, then delete `docs/features/`, `docs/harness/validate_harness.py`, and the `grill-me`, `define-feature`, and `implement-feature` skills from `.claude/skills/` and `.agents/skills/`. Also delete any leftovers from older versions (`docs/harness/done-criteria.md`, `docs/runbooks/development-workflow.md`, `.claude/agents/harness-{scout,worker}.md`, and `.claude/agents/harness-verifier.md` and `.codex/agents/harness-verifier.toml`, now `auditor`). Remove ledger and validator commands from `AGENTS.md`.
5. Check: `grep -rn '{{repo:' .claude .codex` prints nothing; `ls .agents/skills/implement/SKILL.md` resolves; `git check-ignore -q .scratch/x .agents/skills .claude/skills/implement/SKILL.md` succeeds; `git diff --check`; the repo's test gate passes.

## Output

```text
AGENTS.md
CLAUDE.md
ARCHITECTURE.md
docs/harness/workflow.md
docs/harness/dashboard.html   (only if the user says yes)
docs/adr/                      (when a boundary exists)
.claude/skills/{grill-with-docs,to-spec,to-tickets,run-tickets,implement,tdd,diagnosing-bugs,handoff,retro}/SKILL.md
.agents/skills -> ../.claude/skills
.claude/agents/auditor.md
.codex/agents/auditor.toml
.gitignore                     (+ .scratch/, .agents/, .claude/)
```
