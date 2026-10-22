---
id: hook-rule.timeouts
kind: hook-rule
status: VERIFIED
title: "Hook timeouts"
sources: [S2]
---

# Hook timeouts

**Sources:** [S2](src.s2.md)

Command, http and mcp_tool hooks are cancelled at their timeout, and their output is dropped. On PreToolUse a timeout does not block. On PreModelSwitch a timeout does block.
