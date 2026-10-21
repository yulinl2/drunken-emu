---
id: mcp.tools-with-invalid-input-schemas
kind: mcp
status: VERIFIED
title: "Tools with invalid input schemas"
sources: [S31]
---

# Tools with invalid input schemas

**Sources:** [S31](src.s31.md)

The Claude API checks every tool's input schema in a request and rejects the whole request when any one schema fails, so a single MCP tool with a malformed schema would make every request that includes it fail with a 400 error. Claude Code runs two of the API's checks itself when it loads a server's tools and excludes each tool that would fail them, so the server's other tools keep working:
