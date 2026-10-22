---
id: feature.connecting-or-removing-an-mcp-server
kind: feature
status: VERIFIED
title: "Connecting or removing an MCP server"
sources: [S18]
---

# Connecting or removing an MCP server

**Sources:** [S18](src.s18.md)

Tool definitions sit in the system prompt layer, so the cache invalidates when the set of tool definitions in the request changes between turns. Toggling the advisor tool is an exception: its definition sits after the cache breakpoint, so enabling or disabling `/advisor` keeps the cached prefix intact. Whether an MCP server change does this depends on whether tool search defers the session's MCP t
