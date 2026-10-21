---
id: mcp.defer-a-server-s-tools
kind: mcp
status: VERIFIED
title: "Defer a server's tools"
sources: [S31]
---

# Defer a server's tools

**Sources:** [S31](src.s31.md)

To keep all of a server's tools behind tool search, set `"alwaysLoad": false` in that server's entry in your MCP configuration. That includes tools that the server's author has marked to load upfront. If you leave `alwaysLoad` out, those marked tools load upfront. Requires Claude Code v2.1.287 or later.
