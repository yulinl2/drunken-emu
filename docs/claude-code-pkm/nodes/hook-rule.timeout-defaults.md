---
id: hook-rule.timeout-defaults
kind: hook-rule
status: VERIFIED
title: "Default timeouts"
sources: [S2]
---

# Default timeouts

**Sources:** [S2](src.s2.md)

Command, http and mcp_tool: 600 s. Prompt: 30 s. Agent: 60 s. On UserPromptSubmit, PreModelSwitch and PostModelSwitch, command, http and mcp_tool: 30 s. MessageDisplay: 10 s. SessionEnd shares a 1.5 s budget, raised to match a longer per-hook timeout of up to 60 s.

## Linked from

- [SessionEnd](hook.session-end.md)
