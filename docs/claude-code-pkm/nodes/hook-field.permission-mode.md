---
id: hook-field.permission-mode
kind: hook-field
status: VERIFIED
title: "permission_mode"
sources: [S85]
---

# permission_mode

**Sources:** [S85](src.s85.md)

Current permission mode: `"default"`, `"plan"`, `"acceptEdits"`, `"auto"`, `"dontAsk"`, or `"bypassPermissions"`. The mode labeled Manual arrives as `"default"`, never as `"manual"`, so scripts that match `"default"` keep working. Not all events receive this field. Check the JSON example in each hook event section
