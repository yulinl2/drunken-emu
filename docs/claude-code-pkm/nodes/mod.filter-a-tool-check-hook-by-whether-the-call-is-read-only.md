---
id: mod.filter-a-tool-check-hook-by-whether-the-call-is-read-only
kind: mod
status: VERIFIED
title: "Filter a tool.check hook by whether the call is read-only"
sources: [S55]
---

# Filter a tool.check hook by whether the call is read-only

**Sources:** [S55](src.s55.md)

To limit which calls your hook handles by `e.isReadOnly`, use the matcher for read-only calls and the hook body for the rest:
