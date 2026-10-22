---
id: mcp.use-a-fixed-oauth-callback-port
kind: mcp
status: VERIFIED
title: "Use a fixed OAuth callback port"
sources: [S31]
---

# Use a fixed OAuth callback port

**Sources:** [S31](src.s31.md)

Some MCP servers require a specific redirect URI registered in advance. By default, Claude Code picks a random available port for the OAuth callback. Use `--callback-port` to fix the port so it matches a pre-registered redirect URI of the form `http://localhost:PORT/callback`. If sign-in on Claude Code v2.1.229 fails with a redirect URI mismatch, see the version note under Use pre-configured OAuth
