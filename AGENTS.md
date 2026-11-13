# AGENTS.md

This repo is the `agentic-engineering` skill: `SKILL.md` tells an agent how to install a harness into a target repo from the templates in `assets/`. It is Markdown plus the Router (`router/`), a Python hook that asks TypeSafe's Jev, through the AI gateway, which model a subagent runs on.

## Before work

- Read `ARCHITECTURE.md`, `SKILL.md`, `references/guide.md`, and the ADRs in `docs/adr/`.
- Preserve unrelated changes in the working tree.

## Invariants

- `assets/` is the product: keep it target-agnostic and keep its `{{repo: ...}}` markers; never fill them there.
- `.claude/`, `.codex/` and `.agents/` are this repo's own installed harness. Editing `assets/` does not update them; rerun `/agentic-engineering` here when a template change should apply to this repo too.
- Claude files are the single source; Codex reads them through the `.agents/skills` symlink and `.codex/agents/harness-verifier.toml`, a pointer. Never write a second copy (ADR 0001).
- Adding, renaming or removing an installed file changes `SKILL.md` Install, `SKILL.md` Output and the frontmatter `description` together.
- Keep the MIT attribution comment at the top of every adapted skill and of `SKILL.md`.
- The Router sends the gateway only `subagent_type` and the redacted subagent prompt (first 4,000 characters), reads the endpoint from `AIGW_BASE` (else `ANTHROPIC_BASE_URL`) and the service key only from `AIGW_API_KEY`, changes nothing but `model`, and never touches a call where the caller or the agent's definition chose a model.
- The Router is not part of the product: `SKILL.md` and `assets/` do not install it.
- Generated guides stay short and operational: no generic advice, no transient plans (`references/guide.md`).

## Commands

- Test gate (offline, stdlib only, Python 3.11+): `python3 -m unittest discover -s tests`
- Install the Router on this machine: `uv tool install --system-certs --force ./router`; it is registered user-wide as a `PreToolUse` hook on `Agent` in `~/.claude/settings.json` and logs to `~/.local/state/jev-router/decisions.jsonl`.
- Router cost and speed, with and without it (opt-in: billed `claude -p` calls): `python3 router/bench_cost.py --runs N`; results in `.scratch/bench/`.
- Install checks after a dry run in a target repo: `SKILL.md` step 5.

## Patterns

- Copy `assets/skills/to-tickets/SKILL.md` for a new skill: `name` and `description` frontmatter, attribution comment, one H1.
- Copy `assets/agents/harness-verifier.toml` for a Codex agent: a pointer to its Markdown file, no instructions of its own.
- Do not reintroduce feature ledgers or validators (`docs/features/`, `validate_harness.py`); `SKILL.md` step 4 deletes them.

## Workflow

`/grill-with-docs` (only when unclear) -> `/to-spec` (ephemeral `.scratch/<slug>/spec.md`; skip for small fixes) -> `/implement <spec>`. Bugs start with `/diagnosing-bugs`. Details: `docs/harness/workflow.md`.

`.agents/skills` is a symlink to `.claude/skills`; edit once.

When corrected twice, or after 2+ repairs for the same mistake, add an Invariant or Pattern here.
