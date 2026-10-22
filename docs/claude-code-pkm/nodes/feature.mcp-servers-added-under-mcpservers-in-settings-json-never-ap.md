---
id: feature.mcp-servers-added-under-mcpservers-in-settings-json-never-ap
kind: feature
status: VERIFIED
title: "MCP servers added under mcpServers in settings.json never appear"
sources: [S40]
---

# MCP servers added under mcpServers in settings.json never appear

**Sources:** [S40](src.s40.md)

cause: `settings.json` does not read an `mcpServers` key; fix: Define project servers in `.mcp.json` at the repository root, or run `claude mcp add --scope user` for user-scoped servers. See MCP configuration.
