---
id: feature.mcp-server-starts-without-expected-environment-variables
kind: feature
status: VERIFIED
title: "MCP server starts without expected environment variables"
sources: [S40]
---

# MCP server starts without expected environment variables

**Sources:** [S40](src.s40.md)

cause: The server's config entry doesn't set them, and they aren't in the environment Claude Code passes to stdio servers: its own environment, minus the variables it strips from subprocesses; fix: Set per-server `env` inside the server's `.mcp.json` entry, which doesn't depend on the launch environment or workspace trust.
