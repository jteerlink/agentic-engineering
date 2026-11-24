# Architecture

## Purpose

A skill that a coding agent (Claude Code or Codex) runs inside a target repo to write that repo's agent harness: guides, workflow, skills and an auditor agent. No code runs at install time; the agent follows `skills/agentic-engineering/SKILL.md`.

## Components

| id | code | responsibility | paths | start here |
|---|---|---|---|---|
| installer | `skills/agentic-engineering/SKILL.md` | Install steps, output list, checks | `skills/agentic-engineering/SKILL.md` | `skills/agentic-engineering/SKILL.md` |
| guide | Markdown | How to write `AGENTS.md`, `ARCHITECTURE.md`, ADRs and docs tests | `skills/agentic-engineering/references/` | `skills/agentic-engineering/references/guide.md` |
| workflow | Markdown template | The loop and phase-boundary rules | `skills/agentic-engineering/assets/workflow.md` | `skills/agentic-engineering/assets/workflow.md` |
| skills | Markdown templates | grill-with-docs, to-spec, to-tickets, run-tickets, implement, tdd, diagnosing-bugs, handoff, retro | `skills/agentic-engineering/assets/skills/` | `skills/agentic-engineering/assets/skills/implement.md` |
| dashboard | Static HTML + inline JS (optional install) | Read-only ticket board polling `.scratch` tickets over a localhost `http.server` | `skills/agentic-engineering/assets/dashboard.html` | `skills/agentic-engineering/assets/dashboard.html` |
| auditor | Markdown + TOML pointer | Fresh-context auditor (Spec and Standards axes) | `skills/agentic-engineering/assets/agents/` | `skills/agentic-engineering/assets/agents/auditor.md` |
| codex-ui | YAML | Display name and default prompt in Codex | `skills/agentic-engineering/agents/openai.yaml` | `skills/agentic-engineering/agents/openai.yaml` |
| plugin | JSON manifests | Make the repo installable as a Claude Code and a Codex plugin that ships only the installer skill | `.claude-plugin/`, `.codex-plugin/`, `.agents/plugins/` | `.codex-plugin/plugin.json` |
| own-harness | Filled copies of the templates | This repo's harness | `.claude/`, `.codex/`, `.agents/skills`, `docs/harness/` | `AGENTS.md` |
| tests | Python stdlib | Docs paths, single-source mirrors, markers, attribution, auditor model pin, SKILL.md lists every skill, dashboard self-contained, plugin ships one skill, manifests agree | `tests/` | `tests/test_harness.py` |

## Flow

User runs `/agentic-engineering` in a target repo -> agent reads `skills/agentic-engineering/SKILL.md` and `skills/agentic-engineering/references/guide.md` -> discovers the target -> writes guides and copies `skills/agentic-engineering/assets/` with `{{repo: ...}}` markers filled -> runs the step 5 checks.

## Contracts

- The Output list in `skills/agentic-engineering/SKILL.md` is what a target repo receives.
- `{{repo: ...}}` marks every target-specific value in a template; none may survive in an installed `.claude/` or `.codex/`.
- Templates are `assets/skills/<name>.md`, never `assets/skills/<name>/SKILL.md`: Codex loads every SKILL.md under a plugin's `skills/`, so an unfilled template would ship as a live skill.
- Skill names are slash commands referenced across templates; renaming one means updating every reference.

## Boundaries

- The skill instructs an agent with write access to the target repo; templates must not carry another repo's names, commands or secrets.
- `/run-tickets` may commit, push and open or update one draft PR per spec; it never merges. Ticket text is untrusted input to the dashboard, which is served from `.scratch/` on 127.0.0.1 only.

## Known unknowns

- Distribution: how the skill reaches `~/.claude/skills/` or Codex is not recorded in the repo.
