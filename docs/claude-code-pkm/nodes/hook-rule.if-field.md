---
id: hook-rule.if-field
kind: hook-rule
status: VERIFIED
title: "Hook field: if"
sources: [S2]
---

# Hook field: if

**Sources:** [S2](src.s2.md)

The if field takes one permission-rule expression, such as Bash(git *). It runs only on PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest and PermissionDenied. On other events the hook never runs.

## Linked from

- [PreToolUse](hook.pre-tool-use.md)
