---
id: hook-field.permissiondecision
kind: hook-field
status: VERIFIED
title: "permissionDecision"
sources: [S85]
---

# permissionDecision

**Sources:** [S85](src.s85.md)

`"allow"` skips the permission prompt, except for actions no mode auto-approves and reads from network paths. `AskUserQuestion` and `ExitPlanMode` need `updatedInput` paired with `"allow"`. For plan mode, see Hook approvals in plan mode. `"deny"` prevents the tool call. `"ask"` prompts the user to confirm. `"defer"` ends the turn so the tool can be resumed later, and requires non-interactive mode with the `-p` flag. Deny and ask rules are still evaluated regardless of what the hook returns
