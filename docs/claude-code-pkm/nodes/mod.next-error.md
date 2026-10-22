---
id: mod.next-error
kind: mod
status: VERIFIED
title: "next.error"
sources: [S54]
---

# next.error

**Sources:** [S54](src.s54.md)

In a `.catch` handler only. `kind` is `throw` or `timeout` when the hook failed, and `message` is the error's text. `kind` is `re-entry` when the hook was skipped because the event came from inside a mods API call by that hook or by your mod's code outside its hooks. `re-entry` requires Claude Code v2.1.292 or later.
