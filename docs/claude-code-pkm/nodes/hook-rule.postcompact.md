---
id: hook-rule.postcompact
kind: hook-rule
status: VERIFIED
title: "PostCompact"
sources: [S85]
---

# PostCompact

**Sources:** [S85](src.s85.md)

Runs after Claude Code completes a compact operation. Use this event to react to the new compacted state, for example to log the generated summary or update external state. Claude Code discards a PostCompact hook's `systemMessage` and `continue` fields.
