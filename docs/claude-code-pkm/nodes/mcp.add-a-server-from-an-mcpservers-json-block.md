---
id: mcp.add-a-server-from-an-mcpservers-json-block
kind: mcp
status: VERIFIED
title: "Add a server from an mcpServers JSON block"
sources: [S31]
---

# Add a server from an mcpServers JSON block

**Sources:** [S31](src.s31.md)

An `mcpServers` block written for another MCP client, such as Claude Desktop, uses the wrapper key and entry shape Claude Code reads. Pass `claude mcp add-json` the object inside `mcpServers`, not the wrapper. Two entries need a repair first:
