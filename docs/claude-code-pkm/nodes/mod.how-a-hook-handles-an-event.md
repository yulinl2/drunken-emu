---
id: mod.how-a-hook-handles-an-event
kind: mod
status: VERIFIED
title: "How a hook handles an event"
sources: [S55]
---

# How a hook handles an event

**Sources:** [S55](src.s55.md)

A hook sits between an event and what Claude Code would do about it, so it can observe the event, rewrite it, or answer it itself. It receives three arguments: the mods API as `$`, the event as `e`, and the next handler as `next`. The handlers for an event form a middleware chain. `next(e)` calls the next handler, which is another mod's hook or, at the end of the chain, Claude Code's own behavior,
