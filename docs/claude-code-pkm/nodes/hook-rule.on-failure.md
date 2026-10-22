---
id: hook-rule.on-failure
kind: hook-rule
status: VERIFIED
title: "Field: onFailure"
sources: [S2]
---

# Field: onFailure

**Sources:** [S2](src.s2.md)

For command and http hooks (v2.1.295 or later). continue is the default. block acts like exit 2 on that event, and on PermissionRequest it denies. No effect on Stop, SubagentStop, TaskCompleted, TeammateIdle, or async hooks.
