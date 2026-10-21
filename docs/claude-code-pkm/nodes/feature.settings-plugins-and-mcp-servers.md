---
id: feature.settings-plugins-and-mcp-servers
kind: feature
status: VERIFIED
title: "Settings, plugins, and MCP servers"
sources: [S26]
---

# Settings, plugins, and MCP servers

**Sources:** [S26](src.s26.md)

Agent view accepts the same configuration flags as `claude` for loading settings, plugins, MCP servers, and additional directories. Agent view applies `--settings`, `--setting-sources`, and `--plugin-dir` to itself and passes every configuration flag through to the sessions you dispatch from it, so a plugin or MCP server you load this way is available in those sessions.
