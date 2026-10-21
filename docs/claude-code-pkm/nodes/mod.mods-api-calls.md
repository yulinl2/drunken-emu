---
id: mod.mods-api-calls
kind: mod
status: VERIFIED
title: "Mods API calls"
sources: [S54]
---

# Mods API calls

**Sources:** [S54](src.s54.md)

Every mods API method is also an event, named for its namespace and method, such as `fs.read`, `model.complete`, or `ui.open`. A hook on one intercepts calls from the mods that run after it, and can return `next(e)`, `{ deny: reason }`, or `{ value }`.
