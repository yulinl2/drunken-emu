---
id: env.claude-code-mcp-startup-wait-ms
kind: env
status: VERIFIED
title: "CLAUDE_CODE_MCP_STARTUP_WAIT_MS"
sources: [S81]
---

# CLAUDE_CODE_MCP_STARTUP_WAIT_MS

**Sources:** [S81](src.s81.md)

How long in milliseconds the first turn of a non-interactive session waits for MCP servers that are still connecting, in place of the default first-turn wait. In a self-hosted environment, it changes only how long the wait lasts. Some servers keep a wait of their own regardless of the value; Connection timing lists them. Set to `0` to skip the wait for every other server. Requires Claude Code v2.1.274 or later
