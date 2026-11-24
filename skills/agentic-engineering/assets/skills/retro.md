---
name: retro
description: Retrospective on a coding session that proposes environment improvements (checks, navigation pointers, auditor rules, AGENTS.md pruning), then deletes merged specs and tickets from .scratch/ after the user confirms. User-invoked.
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

## Clean up merged work

Plans are deleted after merge, and this is where that happens. In the main checkout (the first path in `git worktree list`), list each `.scratch/<slug>/` folder whose `spec.md` says `Status: done` and whose tickets, if any, all say `done`. A folder counts as merged when its PR shows `MERGED`: check the `PR:` URL in its tickets with `gh pr view <url> --json state`, or else `gh pr list --head tickets/<slug> --state merged`. Show the user the list, split into merged and done-but-merge-unknown. `.scratch/` is gitignored, so deleting it cannot be undone: delete only the folders the user confirms. For each, also run `git worktree remove .claude/worktrees/<slug>` and `git branch -D tickets/<slug>` if they exist. Never touch a folder whose spec or any ticket is not `done`.
