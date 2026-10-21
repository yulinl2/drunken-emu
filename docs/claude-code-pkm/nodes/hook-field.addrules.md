---
id: hook-field.addrules
kind: hook-field
status: VERIFIED
title: "addRules"
sources: [S85]
---

# addRules

**Sources:** [S85](src.s85.md)

Adds permission rules. `rules` is an array of `{toolName, ruleContent?}` objects. Omit `ruleContent` to match the whole tool. `behavior` is `"allow"`, `"deny"`, or `"ask"` (fields: `rules`, `behavior`, `destination`)
