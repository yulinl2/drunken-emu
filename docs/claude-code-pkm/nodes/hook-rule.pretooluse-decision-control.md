---
id: hook-rule.pretooluse-decision-control
kind: hook-rule
status: VERIFIED
title: "PreToolUse decision control"
sources: [S85]
---

# PreToolUse decision control

**Sources:** [S85](src.s85.md)

`PreToolUse` hooks can control whether a tool call proceeds. Unlike other hooks that use a top-level `decision` field, PreToolUse returns its decision inside a `hookSpecificOutput` object. This gives it richer control: four outcomes (allow, deny, ask, or defer) plus the ability to modify tool input before execution.
