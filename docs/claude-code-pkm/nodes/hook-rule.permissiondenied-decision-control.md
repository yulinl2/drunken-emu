---
id: hook-rule.permissiondenied-decision-control
kind: hook-rule
status: VERIFIED
title: "PermissionDenied decision control"
sources: [S85]
---

# PermissionDenied decision control

**Sources:** [S85](src.s85.md)

PermissionDenied hooks can tell the model it may retry the denied tool call. Return a JSON object with `hookSpecificOutput.retry` set to `true`:
