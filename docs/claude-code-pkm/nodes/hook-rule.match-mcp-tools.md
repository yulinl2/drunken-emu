---
id: hook-rule.match-mcp-tools
kind: hook-rule
status: VERIFIED
title: "Match MCP tools"
sources: [S85]
---

# Match MCP tools

**Sources:** [S85](src.s85.md)

MCP server tools appear as regular tools in tool events (`PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied`), so you can match them the same way you match any other tool name.
