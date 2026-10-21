---
id: plugin.mcp-servers
kind: plugin
status: VERIFIED
title: "MCP servers"
sources: [S45]
---

# MCP servers

**Sources:** [S45](src.s45.md)

An MCP server gives Claude tools from an external system. Declare it in `.mcp.json` at the plugin root, in the same shape as a project `.mcp.json`. This `.mcp.json` declares one server named `db`:
