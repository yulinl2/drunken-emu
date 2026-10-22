---
id: mod.the-e-isreadonly-field-on-tool-check
kind: mod
status: VERIFIED
title: "The e.isReadOnly field on tool.check"
sources: [S54]
---

# The e.isReadOnly field on tool.check

**Sources:** [S54](src.s54.md)

In a `tool.check` hook, `e.isReadOnly` is `true` when the tool reports this call as read-only. Otherwise the field is absent, not `false`. The value is the tool's own report, so read Check whether a tool call is read-only before you approve a call on this field alone.
