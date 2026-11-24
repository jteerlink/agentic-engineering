---
name: retro
description: Retrospective on a coding session that proposes environment improvements (checks, navigation pointers, auditor rules, AGENTS.md pruning). User-invoked.
---

<!-- Adapted from mattpocock/skills (retro), MIT License, Copyright (c) 2026 Matt Pocock -->

# Retro

Suggest changes to the agent's **environment** that would make future sessions better. Read the session the user names, or the current one by default, then present candidates ordered by severity. Edit only what the user approves.

- **Automated checks:** an agent mistake that follows a fixed pattern (banned import, hard-coded constant, wrong file location) gets a deterministic check: an offline test, a lint rule, a CI step, or a hook. Prefer building the check to writing a rule. Check first for an existing check that is broken or not wired in.
- **Auditor rules:** if `auditor` missed a judgment-call mistake, add a rule to its Standards axis. The reviewer, which only reads the diff, should enforce standards, so the implementer doesn't have to carry them.
- **Navigation:** if the agent spent a long time finding something, add a one-line pointer to `AGENTS.md`, or link the doc that answers it.
- **AGENTS.md pruning:** move rules that a check now enforces out of `AGENTS.md`, and delete instructions that change nothing.
- **Domain knowledge:** missing terms go in `GLOSSARY.md`, and unrecorded hard-to-reverse decisions go in `docs/adr/`.
- **Information access:** if something the agent needed was unavailable (logs, a read-only query, a fixture), say what would have made it available.
- **Harness pruning:** every harness step assumes the model can't do something on its own. Name any step (a skill phase, an auditor check, a rule) that caught or changed nothing in recent sessions, and propose dropping or loosening it. Revisit when the model changes.
- **Tool economy:** flag expensive tool calls or output-heavy commands that could be narrowed.
