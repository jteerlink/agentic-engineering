# Architecture

## Purpose

A skill that a coding agent (Claude Code or Codex) runs inside a target repo to write that repo's agent harness: guides, workflow, skills and a verifier agent. No code runs at install time; the agent follows `SKILL.md`.

## Components

| id | code | responsibility | paths | start here |
|---|---|---|---|---|
| installer | `SKILL.md` | Install steps, output list, checks | `SKILL.md` | `SKILL.md` |
| guide | Markdown | How to write `AGENTS.md`, `ARCHITECTURE.md`, ADRs and docs tests | `references/` | `references/guide.md` |
| workflow | Markdown template | The loop and phase-boundary rules | `assets/workflow.md` | `assets/workflow.md` |
| skills | Markdown templates | grill-with-docs, to-spec, to-tickets, implement, tdd, diagnosing-bugs, handoff, retro | `assets/skills/` | `assets/skills/implement/SKILL.md` |
| verifier | Markdown + TOML pointer | Fresh-context verifier (Spec and Standards axes) | `assets/agents/` | `assets/agents/harness-verifier.md` |
| codex-ui | YAML | Display name and default prompt in Codex | `agents/openai.yaml` | `agents/openai.yaml` |
| own-harness | Filled copies of the templates | This repo's harness | `.claude/`, `.codex/`, `.agents/`, `docs/harness/` | `AGENTS.md` |
| router | Python stdlib | User-wide Claude Code PreToolUse hook on `Agent`: unless a model was chosen, asks Jev (via the AI gateway) to pick haiku, sonnet or opus and rewrites only `model`; logs each decision | `router/` | `router/jev_router.py` |
| tests | Python stdlib | Docs paths, single-source mirrors, markers, attribution; the Router against a stub gateway | `tests/` | `tests/test_router.py` |

## Flow

User runs `/agentic-engineering` in a target repo -> agent reads `SKILL.md` and `references/guide.md` -> discovers the target -> writes guides and copies `assets/` with `{{repo: ...}}` markers filled -> runs the step 5 checks.

## Contracts

- The Output list in `SKILL.md` is what a target repo receives.
- `{{repo: ...}}` marks every target-specific value in a template; none may survive in an installed `.claude/` or `.codex/`.
- Skill names are slash commands referenced across templates; renaming one means updating every reference.

## Boundaries

- The skill instructs an agent with write access to the target repo; templates must not carry another repo's names, commands or secrets.
- The Router is this machine's tool, not part of the skill: it sends redacted subagent tasks to Jev (TypeSafe, a different vendor from Claude) through the AI gateway's decisions endpoint, and on any failure prints nothing, so the subagent runs on its default model. Nothing else uses the network.

## Known unknowns

- Distribution: how the skill reaches `~/.claude/skills/` or Codex is not recorded in the repo.
