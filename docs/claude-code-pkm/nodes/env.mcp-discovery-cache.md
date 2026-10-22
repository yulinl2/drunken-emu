---
id: env.mcp-discovery-cache
kind: env
status: VERIFIED
title: "MCP_DISCOVERY_CACHE"
sources: [S81]
---

# MCP_DISCOVERY_CACHE

**Sources:** [S81](src.s81.md)

Turns the MCP discovery cache on or off. With the cache on, a remote HTTP or SSE server you've used before can show the `cached` status, and Claude Code connects it on its first tool call instead of at startup. The cache is off by default unless a gradual rollout has enabled it for your account. Set to `1` to turn it on, or `0` to keep it off even when the rollout has enabled it. Before v2.1.238, the cache was on by default. The `cached` status requires Claude Code v2.1.221 or later
