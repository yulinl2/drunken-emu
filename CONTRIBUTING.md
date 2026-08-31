# Contributing — for humans and for sessions

This toolkit is maintained by many short-lived agent sessions. The rules below
are scar tissue: a repo worked on without them accumulates hundreds of draft
branches that no one — including their author — can later identify.

1. **`main` carries settled states only.** Drafting happens in a local clone as
   local commits; the remote never sees the iteration. "Iterate locally until
   your factual picture and design logic are stable, *then* upload."
2. **A push is publication, not backup.** Commits are cheap, private, and
   revisable; pushed history is public and fixed forward only. One push per
   settled unit — the natural rhythm is one per session, at the end
   (the `/sleep` pattern: work all day, compress once).
3. **Branches coordinate *between* agents; they do not warehouse one agent's
   drafts.** A session that must hand off unfinished work may push at most one
   `wip/<anchor>` branch for the next session to merge or delete. Branches
   never accumulate.
4. **Never rewrite `main`'s history.** Published mistakes are fixed forward;
   retired claims go to README `## Falsified` with the evidence that killed
   them.
5. **Session rhythm:** wake by reading `docs/OPEN-PROBLEMS.md` (the reading
   order is at the top of the README); sleep by making your at-most-one push.

6. **Allocate problem IDs from content, not from position.** New entries in
   `docs/OPEN-PROBLEMS.md` take the form `P-<first 4 hex of sha1(title)>`:

       printf '%s' 'your problem title' | sha1sum | cut -c1-4

   Sequential numbering assumes one writer. This project has not had one since
   2026-08-30 — three sessions touched the repository within an hour on 08-31 —
   and two sessions opening a problem in parallel both compute the same next
   integer. Rule 4 forbids rewriting `main`, so such a collision is permanent.
   The sibling metascience loop hit exactly this as `NEED-0011` with append-only
   ledger IDs. `P1`–`P10` keep their names forever; the scheme changes only for
   entries opened after this rule.

7. **Move history between machines with `git bundle`, never with `tar` of a
   working tree.** `git remote add` writes the token verbatim into
   `.git/config`, so a tar of the repository root carries a live credential —
   demonstrated, not hypothesised (P8). `git bundle create out.bundle --all`
   carries every commit and ref and no configuration at all.
