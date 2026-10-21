---
id: feature.tool-name-safe
kind: feature
status: VERIFIED
title: "tool_name_safe"
sources: [S65]
---

# tool_name_safe

**Sources:** [S65](src.s65.md)

Form of `tool_name` that carries no user-chosen names. Built-in tool names pass verbatim. MCP tool names appear as `mcp_other`, except tool names matching a few fixed shapes, such as `playwright` tools named `browser_*`, which pass verbatim. Requires Claude Code v2.1.268 or later
