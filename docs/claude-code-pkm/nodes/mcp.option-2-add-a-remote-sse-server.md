---
id: mcp.option-2-add-a-remote-sse-server
kind: mcp
status: VERIFIED
title: "Option 2: Add a remote SSE server"
sources: [S31]
---

# Option 2: Add a remote SSE server

**Sources:** [S31](src.s31.md)

Some services still expose only an SSE endpoint. Add these with the same `claude mcp add --transport http ` command as an HTTP server. Claude Code tries the HTTP transport first and switches to SSE when the server doesn't accept it. The automatic switch requires Claude Code v2.1.265 or later.
