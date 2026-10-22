---
id: mcp.require-approval-for-a-specific-tool
kind: mcp
status: VERIFIED
title: "Require approval for a specific tool"
sources: [S31]
---

# Require approval for a specific tool

**Sources:** [S31](src.s31.md)

If you're building an MCP server, you can mark a tool as requiring explicit approval on every call by setting `_meta["anthropic/requiresUserInteraction"]` to `true` in the tool's `tools/list` response entry. The value must be the JSON Boolean `true`; any other value is ignored.
