---
name: run-tickets
description: Work an approved spec's ticket frontier unattended — each ready ticket through /implement in one worktree, one commit per ticket, one draft PR per spec — and stop at the first blocked ticket. Run as /run-tickets <path-to-spec>. Never merges.
---

# Run Tickets

Running this skill is the user's request to commit, push, and open or update **one draft PR** for this spec. It never merges, never marks the PR ready, and never deploys. The tickets' `Status:` lines and `## Log` sections are the only state; do not add another.

## Setup

1. The main checkout is the first path in `git worktree list`. Tickets live there (`.scratch/<slug>/issues/*.md`), because `.scratch/` is gitignored and does not exist inside a worktree. Read the spec and the tickets.
2. **Board.** If `docs/harness/dashboard.html` exists, make sure the ticket board is up so the user can watch: if `curl -sf http://127.0.0.1:8765/ | grep -q '<slug>/'` fails, run `ln -sf ../docs/harness/dashboard.html .scratch/dashboard.html` in the main checkout, then start `python3 -m http.server 8765 --bind 127.0.0.1 -d .scratch` there in the background so it outlives the run (if port 8765 is taken by something else, use 8766). Leave it running. Tell the user the URL: `http://127.0.0.1:<port>/dashboard.html`.
3. If any ticket is `Status: blocked`, go to **Finish**. A human resolves it first.
4. Worktree: reuse `.claude/worktrees/<slug>` if `git worktree list` shows it. Otherwise, from the main checkout, run `git fetch` and then `git worktree add --no-track .claude/worktrees/<slug> -b tickets/<slug> origin/{{repo: base branch, e.g. main}}`. If branch `tickets/<slug>` already exists, run `git worktree add .claude/worktrees/<slug> tickets/<slug>` instead. Never put it under `.scratch/`, because the dashboard serves that folder.
5. If the worktree has uncommitted changes and no ticket is `building`, stop and report them. They are leftovers nobody owns.
6. If the branch has commits beyond the base, and either its remote lacks some of them or no draft PR exists for it, run **Publish** before picking. A new branch with no commits has nothing to publish yet.

## Loop

1. **Pick.** If a ticket is `Status: building`, a previous run stopped mid-ticket: resume it. Otherwise take the lowest-numbered `ready` ticket whose `Blocked by` tickets are all `done`. If none is left, go to **Finish**.
2. **Build.** Run `/implement <absolute path to the ticket in the main checkout>` inside the worktree.
3. **Check.** Continue only if the ticket now says `Status: done`. Any other status (`blocked`, or still `building` because `/implement` stopped for a red baseline, a spec problem, or an approval gate) goes to **Finish** with its changes left uncommitted.
4. **Commit** the ticket's changes in the worktree (message: the ticket title), then run **Publish**.
5. Back to **Pick**.

## Publish

1. Push with `git push -u origin tickets/<slug>`. If the push fails, go to **Finish** and report it.
2. Look up `gh pr list --head tickets/<slug> --state open --json url`. Run `gh pr create --draft` only if that finds nothing; otherwise run `gh pr edit` to update the body. The body is `/implement`'s PR description, with each `done` ticket's Evidence appended. If `gh` fails, run the lookup again (the PR may already exist) and retry once. If it still fails, go to **Finish** and report it.
3. Add `PR: <url>` under the `Status:` line of each `done` ticket that lacks one.

## Finish

Report each ticket's status, the PR URL, and the next human action:
- review the draft PR;
- resolve the blocked or stopped ticket (quote its Log's root cause and what is left untried), then set it to `Status: building` so the next run resumes it with its uncommitted changes;
- fix a failed push or `gh` step;
- or unblock waiting tickets.
