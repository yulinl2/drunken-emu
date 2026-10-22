---
id: mod.next-error-cause
kind: mod
status: VERIFIED
title: "next.error.cause"
sources: [S54]
---

# next.error.cause

**Sources:** [S54](src.s54.md)

Set only when `kind` is `re-entry`. `rewritten` if a `tool.call` or `PreToolUse` hook changed the mods API call the event came from, or an `agent.spawn` hook changed an agent started by that call. `lent` when a method another mod adds to the mods API fired that event, unless `rewritten` also applies. `lent` requires Claude Code v2.1.292 or later and `rewritten` v2.1.300 or later.
