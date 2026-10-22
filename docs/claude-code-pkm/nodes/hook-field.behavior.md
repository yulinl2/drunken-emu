---
id: hook-field.behavior
kind: hook-field
status: VERIFIED
title: "behavior"
sources: [S85]
---

# behavior

**Sources:** [S85](src.s85.md)

`"allow"` grants the permission, `"deny"` denies it. Deny and ask rules are still evaluated, so a hook returning `"allow"` doesn't override a matching deny rule
