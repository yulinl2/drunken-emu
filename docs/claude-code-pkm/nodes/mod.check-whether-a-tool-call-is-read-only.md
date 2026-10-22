---
id: mod.check-whether-a-tool-call-is-read-only
kind: mod
status: VERIFIED
title: "Check whether a tool call is read-only"
sources: [S55]
---

# Check whether a tool call is read-only

**Sources:** [S55](src.s55.md)

In a `tool.check` hook, `e.isReadOnly` is `true` when the tool reports the call as read-only. Otherwise the field is absent, not `false`. `e.isReadOnly` requires Claude Code v2.1.304 or later.
