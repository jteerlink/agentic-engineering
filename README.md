# agentic-engineering

One command, `/agentic-engineering`, that inspects a repository and installs a short, repo-specific agent harness: `AGENTS.md`, `ARCHITECTURE.md`, a spec → tickets → implement workflow with a fresh-context verifier, and an optional read-only ticket dashboard. It works in Claude Code and Codex.

## Install

Claude Code:

```
/plugin marketplace add jteerlink/agentic-engineering
/plugin install agentic-engineering@agentic-engineering
```

Codex:

```
codex plugin marketplace add jteerlink/agentic-engineering
codex plugin add agentic-engineering@agentic-engineering
```

Then, from the root of the repo you want to set up, run `/agentic-engineering:agentic-engineering` in Claude Code (plugin skills are prefixed with the plugin name), or ask Codex to use the agentic-engineering skill. Rerun it to update an existing harness.

What it writes is listed under Output in [skills/agentic-engineering/SKILL.md](skills/agentic-engineering/SKILL.md).
