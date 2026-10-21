---
id: feature.invalid-values-inside-sandbox
kind: feature
status: VERIFIED
title: "Invalid values inside sandbox"
sources: [S61]
---

# Invalid values inside sandbox

**Sources:** [S61](src.s61.md)

When one value in your managed `sandbox` block is invalid, Claude Code doesn't drop the whole block, because it validates each field on its own. This per-field handling requires Claude Code v2.1.283 or later. On versions before v2.1.283, Claude Code drops every `sandbox` field except `credentials` when a value outside `credentials` is invalid.
