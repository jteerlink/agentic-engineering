---
name: handoff
description: Write a portable handoff file for another agent, harness (Claude <-> Codex), directory, or colleague. Only when work is travelling; otherwise continue or /compact.
argument-hint: "What will the next session be used for?"
---

<!-- Adapted from mattpocock/skills (handoff), MIT License, Copyright (c) 2026 Matt Pocock -->

Write `$TMPDIR/handoff-<slug>.md`, falling back to `/tmp`. Never write it into the repo. It holds:

- **Goal**, plus the next session's focus, taken from the argument if one was given.
- **State:** what works, what failed and why, and what hasn't been tried yet.
- **Pointers** to the spec, ADRs, commits, and diffs. Reference them; don't copy them.
- **Suggested skills** for the next agent.

Redact keys, tokens, and personal data. Don't include row-level production data.
