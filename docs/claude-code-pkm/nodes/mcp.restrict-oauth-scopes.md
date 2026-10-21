---
id: mcp.restrict-oauth-scopes
kind: mcp
status: VERIFIED
title: "Restrict OAuth scopes"
sources: [S31]
---

# Restrict OAuth scopes

**Sources:** [S31](src.s31.md)

Set `oauth.scopes` to pin the scopes Claude Code requests during the authorization flow. This is the supported way to restrict an MCP server to a security-team-approved subset when the upstream authorization server advertises more scopes than you want to grant. The value is a single space-separated string, matching the `scope` parameter format in RFC 6749 §3.3.
