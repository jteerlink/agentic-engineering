# Writing the Harness

## Discovery

Read root guidance (`AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING*`, `README*`), lessons files, ADRs, manifests, lockfiles, CI, deployment config, source and test layout, public interfaces, git status, and any existing harness. Use `rg --files` and targeted `rg`; skip generated, vendored, cache, build, and virtual-environment directories.

Record inspection tools (browser automation, read-only queries, e2e runners) and canonical patterns: the file to copy for each recurring pattern, and legacy code agents should not copy. Flag stale guidance where stated commands or layout contradict manifests or CI.

## `AGENTS.md`

Small and operational; no generic advice or transient plans. Sections:

- **Before work**: what to read first, and to preserve unrelated changes.
- **Invariants**: hard rules agents break (ownership boundaries, forbidden imports, state authorities, required write paths, naming, safety gates), one imperative line each.
- **Commands**: only commands manifests, CI, or scripts support.
- **Inspect**: read-only tools to observe the running system or data before editing. Omit when none exist.
- **Patterns**: `copy X for Y` / `do not copy Z`.
- **Workflow**: one-line flow `/grill-with-docs` (only when unclear) -> `/to-spec` (ephemeral `.scratch/<slug>/spec.md`; skip for small fixes) -> `/implement <spec>`; bugs start with `/diagnosing-bugs`; point to `docs/harness/workflow.md`. Note that `.agents/skills` is a symlink to `.claude/skills` (edit once). Include the self-improvement rule: when corrected twice or needing 2+ repairs for the same mistake, add an Invariant or Pattern.

## `ARCHITECTURE.md`

Current facts (implemented vs. intended kept distinct): purpose, component table (`id`, `code`, `responsibility`, `paths`, `start here`), data/control flows, public contracts, state/trust boundaries, deployment, and known unknowns.

## Knowledge vs. plans

- **Plans are ephemeral.** Specs and tickets live in `.scratch/<slug>/` (gitignored) and are deleted after merge. Proof of done is tests in the repo plus the PR description. No feature ledgers, no validator.
- **`GLOSSARY.md`** is created lazily by `/grill-with-docs` on the first settled domain term: term, one-line meaning, `_Avoid_:` synonyms. Domain language only, no implementation detail.
- **ADRs** (`docs/adr/NNNN-slug.md`, 1–3 sentences; add Consequences only when a future reader needs them) only when a decision is hard to reverse, surprising without context, and a real trade-off. Seed one for any architectural boundary the repo already relies on.
- **Guard a boundary with a test, not a rule.** If an ADR draws a boundary (forbidden import, layer rule), add an offline test that greps for it so CI enforces it. Write the failure message so it tells the agent how to fix the violation and which ADR explains it.
- **Guard the docs too.** Add an offline test that every repo path named in `AGENTS.md` and `ARCHITECTURE.md` exists, with a short allow-list for paths that are deliberately absent.
