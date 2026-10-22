---
id: env.mcp-tool-timeout
kind: env
status: VERIFIED
title: "MCP_TOOL_TIMEOUT"
sources: [S81]
---

# MCP_TOOL_TIMEOUT

**Sources:** [S81](src.s81.md)

Timeout in milliseconds for MCP tool execution (default: 100000000, about 28 hours). For an HTTP, SSE, or claude.ai connector server, each request also times out after 60 seconds by default; set this variable, or the per-server `timeout`, above 60000 to raise that per-request limit. A lower value still shortens the overall tool-execution timeout but leaves the per-request limit at 60 seconds. Stdio and WebSocket servers have no per-request timer. A per-server `timeout` field in `.mcp.json` overrides this for that server. A per-server `timeout` of at least 1000 also sets the minimum idle window for that server's tool calls, so `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT` never aborts them sooner; this floor requires Claude Code v2.1.203 or later. For the env variable, values below 1000 are floored to one second; for the per-server field, values below 1000 are ignored
