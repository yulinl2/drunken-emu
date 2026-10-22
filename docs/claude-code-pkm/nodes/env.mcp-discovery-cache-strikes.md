---
id: env.mcp-discovery-cache-strikes
kind: env
status: VERIFIED
title: "MCP_DISCOVERY_CACHE_STRIKES"
sources: [S81]
---

# MCP_DISCOVERY_CACHE_STRIKES

**Sources:** [S81](src.s81.md)

At a start where a discovery-cache entry is older than `MCP_DISCOVERY_CACHE_TTL_S`, Claude Code refreshes it in the background. This variable sets how many refreshes in a row can fail before Claude Code discards the entry and connects the server at the next start instead (default: 1). Raise it if your network connection drops occasionally, so that one failed refresh doesn't discard the entry. Requires Claude Code v2.1.238 or later
