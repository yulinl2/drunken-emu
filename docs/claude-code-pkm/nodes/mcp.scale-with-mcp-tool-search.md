---
id: mcp.scale-with-mcp-tool-search
kind: mcp
status: VERIFIED
title: "Scale with MCP tool search"
sources: [S31]
---

# Scale with MCP tool search

**Sources:** [S31](src.s31.md)

Tool search keeps MCP context usage low by deferring tool definitions until Claude needs them. Only tool names and server instructions load at session start, so adding more MCP servers has minimal impact on your context window. Claude Code doesn't impose a fixed per-server tool cap; the practical limit is your context window budget.
