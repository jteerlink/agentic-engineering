# Claude files are the single source; Codex points to them

Installed harnesses serve Claude Code and Codex. Instructions live once in the Claude files: `CLAUDE.md` is `@AGENTS.md`, `.agents/skills` is a symlink to `.claude/skills`, and each `.codex/agents/*.toml` only points to its `.md`, because two copies drift. `tests/test_harness.py` enforces this here.
