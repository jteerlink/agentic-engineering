# AGENTS.md

This repo is the `agentic-engineering` skill, shipped as a Claude Code and Codex plugin: `skills/agentic-engineering/SKILL.md` tells an agent how to install a harness into a target repo from the templates in `skills/agentic-engineering/assets/`. It is Markdown plus one static, optional dashboard (`skills/agentic-engineering/assets/dashboard.html`); the Python in `tests/` checks it. Nothing runs at install time.

## Before work

- Read `ARCHITECTURE.md`, `skills/agentic-engineering/SKILL.md`, `skills/agentic-engineering/references/guide.md`, and the ADRs in `docs/adr/`.
- Preserve unrelated changes in the working tree.

## Invariants

- `skills/agentic-engineering/assets/` is the product: keep it target-agnostic and keep its `{{repo: ...}}` markers; never fill them there.
- `.claude/`, `.codex/` and `.agents/skills` are this repo's own installed harness; the plugins never ship them. Editing `skills/agentic-engineering/assets/` does not update them; rerun `/agentic-engineering` here when a template change should apply to this repo too.
- Claude files are the single source; Codex reads them through the `.agents/skills` symlink and `.codex/agents/auditor.toml`, a pointer. Never write a second copy (ADR 0001).
- Adding, renaming or removing an installed file changes `skills/agentic-engineering/SKILL.md` Install, `skills/agentic-engineering/SKILL.md` Output and the frontmatter `description` together.
- Keep the MIT attribution comment at the top of every adapted skill and of `skills/agentic-engineering/SKILL.md`. Original skills (`run-tickets`) are listed in `ORIGINAL_SKILLS` in `tests/test_harness.py` instead.
- `skills/agentic-engineering/assets/dashboard.html` stays self-contained and read-only: no network loads, no `innerHTML` (ticket text is untrusted), served from `.scratch/` only.
- Generated guides stay short and operational: no generic advice, no transient plans (`skills/agentic-engineering/references/guide.md`).

## Commands

- Test gate (offline, stdlib only, Python 3.11+): `python3 -m unittest discover -s tests`
- Plugin check: `claude plugin validate .`
- Release: bump `version` in `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` together; installs are cached per version.
- Install checks after a dry run in a target repo: `skills/agentic-engineering/SKILL.md` step 5.

## Patterns

- Copy `skills/agentic-engineering/assets/skills/to-tickets.md` for a new skill: `name` and `description` frontmatter, attribution comment, one H1. A skill written here (not adapted) drops the comment and joins `ORIGINAL_SKILLS`.
- Copy `skills/agentic-engineering/assets/agents/auditor.toml` for a Codex agent: a pointer to its Markdown file, no instructions of its own.
- Do not reintroduce feature ledgers or validators (`docs/features/`, `validate_harness.py`); `skills/agentic-engineering/SKILL.md` step 4 deletes them.

## Workflow

`/grill-with-docs` (only when unclear) -> `/to-spec` (ephemeral `.scratch/<slug>/spec.md`; skip for small fixes) -> `/implement <spec>`. Bugs start with `/diagnosing-bugs`. Details: `docs/harness/workflow.md`.

`.agents/skills` is a symlink to `.claude/skills`; edit once.

When corrected twice, or after 2+ repairs for the same mistake, add an Invariant or Pattern here.
