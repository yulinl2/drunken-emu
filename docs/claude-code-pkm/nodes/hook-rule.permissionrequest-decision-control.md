---
id: hook-rule.permissionrequest-decision-control
kind: hook-rule
status: VERIFIED
title: "PermissionRequest decision control"
sources: [S85]
---

# PermissionRequest decision control

**Sources:** [S85](src.s85.md)

`PermissionRequest` hooks can allow or deny permission requests. In addition to the JSON output fields available to all hooks, your hook script can return a `decision` object with these event-specific fields:
