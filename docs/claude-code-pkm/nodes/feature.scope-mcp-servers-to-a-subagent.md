---
id: feature.scope-mcp-servers-to-a-subagent
kind: feature
status: VERIFIED
title: "Scope MCP servers to a subagent"
sources: [S25]
---

# Scope MCP servers to a subagent

**Sources:** [S25](src.s25.md)

Use the `mcpServers` field to give a subagent access to MCP servers that aren't available in the main conversation. Inline servers defined here are connected when the subagent starts, subject to the trust rule for the agent file's folder, and disconnected when it finishes. String references share the parent session's connection.
