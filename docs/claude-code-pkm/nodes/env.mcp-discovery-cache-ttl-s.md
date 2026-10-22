---
id: env.mcp-discovery-cache-ttl-s
kind: env
status: VERIFIED
title: "MCP_DISCOVERY_CACHE_TTL_S"
sources: [S81]
---

# MCP_DISCOVERY_CACHE_TTL_S

**Sources:** [S81](src.s81.md)

Seconds for which Claude Code uses a discovery-cache entry without refreshing it (default: 900). At a start where the entry is older than that, Claude Code still uses it but refreshes it in the background. Once the entry is older than `MCP_DISCOVERY_CACHE_MAX_STALE_S`, Claude Code discards it instead. Claude Code caps the value at `MCP_DISCOVERY_CACHE_MAX_STALE_S`, which is 4 hours by default. Before v2.1.238, Claude Code didn't cap the value
