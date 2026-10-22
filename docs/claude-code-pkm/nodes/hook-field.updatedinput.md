---
id: hook-field.updatedinput
kind: hook-field
status: VERIFIED
title: "updatedInput"
sources: [S85]
---

# updatedInput

**Sources:** [S85](src.s85.md)

Modifies the tool's input parameters before execution. Replaces the entire input object, so include unchanged fields alongside modified ones. Claude Code evaluates permission rules and a Bash command's auto-background eligibility against the input your hook returns, not the input Claude sent. Combine with `"allow"` to auto-approve, or `"ask"` to show the modified input to the user. For `"defer"`, ignored

## Linked from

- [updatedInput](hook-field.updatedinput-hooks.md)
