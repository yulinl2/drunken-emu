---
id: hook-rule.posttoolusefailure-decision-control
kind: hook-rule
status: VERIFIED
title: "PostToolUseFailure decision control"
sources: [S85]
---

# PostToolUseFailure decision control

**Sources:** [S85](src.s85.md)

`PostToolUseFailure` hooks can provide context to Claude after a tool failure. In addition to the JSON output fields available to all hooks, your hook script can return these event-specific fields:
