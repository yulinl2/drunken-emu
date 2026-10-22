---
id: hook-field.impossible
kind: hook-field
status: VERIFIED
title: "impossible"
sources: [S85]
---

# impossible

**Sources:** [S85](src.s85.md)

Optional. The model returns it with `ok: false` when it judges the condition can never be satisfied. On `Stop` and `SubagentStop`, Claude Code then lets the turn end instead of feeding the reason back. Agent hooks and other events ignore it
