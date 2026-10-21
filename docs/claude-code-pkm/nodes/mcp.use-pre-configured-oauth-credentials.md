---
id: mcp.use-pre-configured-oauth-credentials
kind: mcp
status: VERIFIED
title: "Use pre-configured OAuth credentials"
sources: [S31]
---

# Use pre-configured OAuth credentials

**Sources:** [S31](src.s31.md)

Some MCP servers don't support automatic OAuth setup via Dynamic Client Registration. If you see an error like "Incompatible auth server: does not support dynamic client registration," the server requires pre-configured credentials. Claude Code also supports servers that use a Client ID Metadata Document (CIMD) instead of Dynamic Client Registration, and discovers these automatically. If automatic
