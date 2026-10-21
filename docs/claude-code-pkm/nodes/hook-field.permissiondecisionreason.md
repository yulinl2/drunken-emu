---
id: hook-field.permissiondecisionreason
kind: hook-field
status: VERIFIED
title: "permissionDecisionReason"
sources: [S85]
---

# permissionDecisionReason

**Sources:** [S85](src.s85.md)

For `"ask"`, shown to the user in the permission prompt. When Claude Code denies the call in a `-p` run where no one can answer that prompt, Claude reads the reason in the tool result instead. For `"deny"`, shown to Claude. For `"allow"` and `"defer"`, written to the debug log only
