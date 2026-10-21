---
id: env.claude-code-mcp-tool-idle-timeout
kind: env
status: VERIFIED
title: "CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT"
sources: [S81]
---

# CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT

**Sources:** [S81](src.s81.md)

Idle timeout in milliseconds for MCP tool calls. When a stdio, HTTP, SSE, WebSocket, or claude.ai connector MCP server sends no response and no progress notification for this long, the tool call aborts with an error instead of waiting for the overall `MCP_TOOL_TIMEOUT`. Overrides the per-transport defaults of 300000 (5 minutes) for network servers and 1800000 (30 minutes) for stdio servers. Set to `0` to disable the idle check. Values below 1000 are raised to one second, and the value is capped at the effective `MCP_TOOL_TIMEOUT`. A per-server `timeout` in `.mcp.json` of at least 1000 raises that server's idle window to at least the `timeout` value. Doesn't apply to IDE servers or SDK in-process servers. Requires Claude Code v2.1.187 or later. Before v2.1.203, stdio servers were exempt from the idle timeout
