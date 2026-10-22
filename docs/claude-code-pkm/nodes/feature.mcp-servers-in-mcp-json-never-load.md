---
id: feature.mcp-servers-in-mcp-json-never-load
kind: feature
status: VERIFIED
title: "MCP servers in .mcp.json never load"
sources: [S40]
---

# MCP servers in .mcp.json never load

**Sources:** [S40](src.s40.md)

cause: File is under `.claude/`, or its servers sit under a top-level `servers` key, as in VS Code's `mcp.json`, instead of `mcpServers`; fix: Project MCP config goes at the repository root as `.mcp.json`, not inside `.claude/`, with servers under the `mcpServers` key. See MCP configuration.
