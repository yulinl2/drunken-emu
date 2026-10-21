---
id: mcp.use-dynamic-headers-for-custom-authentication
kind: mcp
status: VERIFIED
title: "Use dynamic headers for custom authentication"
sources: [S31]
---

# Use dynamic headers for custom authentication

**Sources:** [S31](src.s31.md)

If your MCP server uses an authentication scheme other than OAuth, such as Kerberos, short-lived tokens, or an internal SSO, use `headersHelper` to generate request headers at connection time. Claude Code runs the command and merges its output into the connection headers.
