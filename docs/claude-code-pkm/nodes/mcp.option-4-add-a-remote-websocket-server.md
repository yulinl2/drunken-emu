---
id: mcp.option-4-add-a-remote-websocket-server
kind: mcp
status: VERIFIED
title: "Option 4: Add a remote WebSocket server"
sources: [S31]
---

# Option 4: Add a remote WebSocket server

**Sources:** [S31](src.s31.md)

WebSocket servers hold a persistent bidirectional connection, which suits remote MCP servers that push events to Claude unprompted. Use HTTP instead when your server only responds to requests, since HTTP supports OAuth and the `claude mcp add --transport` flag, while WebSocket supports neither.
