---
id: mcp.server-status-detail
kind: mcp
status: VERIFIED
title: "Server status detail"
sources: [S31]
---

# Server status detail

**Sources:** [S31](src.s31.md)

In `/mcp`, including a server's menu there, and in the `/plugin` manager, a remote HTTP or SSE server you've used before can show a `cached` status such as `cached 2h ago · connects on first use · 5 tools`. Claude Code loaded the server's tool list from its discovery cache, saved in a previous session, instead of connecting at startup, and Claude Code connects the server the first time Claude call
