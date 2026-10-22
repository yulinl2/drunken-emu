---
id: mod.events
kind: mod
status: VERIFIED
title: "Events"
sources: [S54]
---

# Events

**Sources:** [S54](src.s54.md)

Events are grouped by what they concern, each with when it fires and what a hook on it can return. Hooks on `turn.step` and `process.spawn` are async generators, and other hooks are async functions.
