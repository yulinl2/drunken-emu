---
id: mod.handle-a-hook-that-fails
kind: mod
status: VERIFIED
title: "Handle a hook that fails"
sources: [S55]
---

# Handle a hook that fails

**Sources:** [S55](src.s55.md)

A hook that fails doesn't break the session, and you can decide what happens instead. When a hook with no `.catch` handler throws, times out, or returns a result of the wrong shape, what happens next depends on whether it had called `next`:
