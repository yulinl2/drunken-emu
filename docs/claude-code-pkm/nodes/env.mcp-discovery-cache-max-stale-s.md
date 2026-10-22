---
id: env.mcp-discovery-cache-max-stale-s
kind: env
status: VERIFIED
title: "MCP_DISCOVERY_CACHE_MAX_STALE_S"
sources: [S81]
---

# MCP_DISCOVERY_CACHE_MAX_STALE_S

**Sources:** [S81](src.s81.md)

Maximum age, in seconds, of a discovery-cache entry (default: 14400, or 4 hours). At a start where the entry is older than that, Claude Code discards it and connects the server at startup, as it does with the cache off. Claude Code caps the value at 7 days. Before v2.1.238, the default was 86400, or 24 hours, and Claude Code didn't cap the value
