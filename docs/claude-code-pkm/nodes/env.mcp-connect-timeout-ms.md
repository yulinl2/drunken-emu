---
id: env.mcp-connect-timeout-ms
kind: env
status: VERIFIED
title: "MCP_CONNECT_TIMEOUT_MS"
sources: [S81]
---

# MCP_CONNECT_TIMEOUT_MS

**Sources:** [S81](src.s81.md)

How long blocking MCP startup waits, in milliseconds, for the connection batch before snapshotting the tool list (default: 5000). Applies when `MCP_CONNECTION_NONBLOCKING=0` or for servers marked `alwaysLoad: true`. Servers still pending at the deadline keep connecting in the background. Distinct from `MCP_TIMEOUT`, which bounds an individual server's connect attempt
