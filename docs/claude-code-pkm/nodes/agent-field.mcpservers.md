---
id: agent-field.mcpservers
kind: agent-field
status: VERIFIED
title: "mcpServers"
sources: [S25]
---

# mcpServers

**Sources:** [S25](src.s25.md)

MCP servers available to this subagent. Each entry is either a server name referencing an already-configured server (e.g., `"slack"`) or an inline definition with the server name as key and a full MCP server config as value. Ignored for plugin subagents (required: No)
