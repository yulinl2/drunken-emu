---
id: hook-rule.hook-handler-fields
kind: hook-rule
status: VERIFIED
title: "Hook handler fields"
sources: [S85]
---

# Hook handler fields

**Sources:** [S85](src.s85.md)

Each object in the inner `hooks` array is a hook handler: the shell command, HTTP endpoint, MCP tool, LLM prompt, or agent that runs when the matcher matches. There are five types:
