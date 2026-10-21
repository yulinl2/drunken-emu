---
id: mcp.failed-first-connections
kind: mcp
status: VERIFIED
title: "Failed first connections"
sources: [S31]
---

# Failed first connections

**Sources:** [S31](src.s31.md)

When an HTTP or SSE server's first connection fails with a transient error, such as a 5xx response, a connection refused, or a timeout, Claude Code retries up to three times. If the connection still fails, Claude Code marks the server as failed.
