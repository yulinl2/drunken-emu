---
id: mcp.override-oauth-metadata-discovery
kind: mcp
status: VERIFIED
title: "Override OAuth metadata discovery"
sources: [S31]
---

# Override OAuth metadata discovery

**Sources:** [S31](src.s31.md)

Point Claude Code at a specific OAuth authorization server metadata URL to bypass the default discovery chain. Set `authServerMetadataUrl` when the MCP server's standard endpoints error, or when you want to route discovery through an internal proxy. By default, Claude Code first checks RFC 9728 Protected Resource Metadata at `/.well-known/oauth-protected-resource`, then falls back to RFC 8414 auth
