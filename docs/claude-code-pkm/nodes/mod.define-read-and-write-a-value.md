---
id: mod.define-read-and-write-a-value
kind: mod
status: VERIFIED
title: "Define, read, and write a value"
sources: [S57]
---

# Define, read, and write a value

**Sources:** [S57](src.s57.md)

In your module, define each value with a default, read it while drawing, and write it from a callback. `atom` names a value and its default, `read` returns it, and `update` writes it. The three helpers call `$.state.get` and `$.state.set` for you:
