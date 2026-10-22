---
id: mcp.automatic-reconnection
kind: mcp
status: VERIFIED
title: "Automatic reconnection"
sources: [S31]
---

# Automatic reconnection

**Sources:** [S31](src.s31.md)

Claude Code reconnects a remote server that drops mid-session and retries an HTTP or SSE server's first connection after a transient error. Stdio servers are local processes, and Claude Code doesn't reconnect them automatically.
