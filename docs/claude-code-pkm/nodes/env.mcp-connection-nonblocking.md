---
id: env.mcp-connection-nonblocking
kind: env
status: VERIFIED
title: "MCP_CONNECTION_NONBLOCKING"
sources: [S81]
---

# MCP_CONNECTION_NONBLOCKING

**Sources:** [S81](src.s81.md)

Controls whether startup waits for MCP servers to connect before the first query. MCP startup is non-blocking by default: servers connect in the background and their tools become available as they finish. Set to `0` to make Claude Code wait for servers to connect before the first query. Servers configured with `alwaysLoad: true` still make startup wait regardless, except when served from the discovery cache, since their tools must be present when the first prompt is built. In non-interactive mode (`-p`) without `--input-format stream-json`, Claude Code also waits for still-pending servers before the first turn regardless of this variable. When you pass `--mcp-config` explicitly, the wait has a longer deadline; see that flag's entry for the cached-server exception
