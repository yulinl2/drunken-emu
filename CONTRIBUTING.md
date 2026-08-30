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
