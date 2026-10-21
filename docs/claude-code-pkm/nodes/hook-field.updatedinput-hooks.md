---
id: hook-field.updatedinput-hooks
kind: hook-field
status: VERIFIED
title: "updatedInput"
sources: [S85]
---

# updatedInput

**Sources:** [S85](src.s85.md)

For `"allow"` only: modifies the tool's input parameters before execution. Replaces the entire input object, so include unchanged fields alongside modified ones. The modified input is re-evaluated against deny and ask rules
