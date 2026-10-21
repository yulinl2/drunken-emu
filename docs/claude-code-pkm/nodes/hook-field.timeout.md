---
id: hook-field.timeout
kind: hook-field
status: VERIFIED
title: "timeout"
sources: [S85]
---

# timeout

**Sources:** [S85](src.s85.md)

Seconds before canceling. Claude Code doesn't enforce it on a command hook you run with `async: true`. Defaults: 600 for `command`, `http`, and `mcp_tool`; 30 for `prompt`; 60 for `agent`. Claude Code lowers the `command`, `http`, and `mcp_tool` default to 30 on `UserPromptSubmit`, `PreModelSwitch`, and `PostModelSwitch`, and to 10 on `MessageDisplay`. `SessionEnd` hooks share a 1.5-second budget; if your settings set a longer per-hook `timeout`, Claude Code raises the budget to match, up to 60 seconds (required: no)
