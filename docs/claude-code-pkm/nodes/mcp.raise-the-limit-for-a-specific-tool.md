---
id: mcp.raise-the-limit-for-a-specific-tool
kind: mcp
status: VERIFIED
title: "Raise the limit for a specific tool"
sources: [S31]
---

# Raise the limit for a specific tool

**Sources:** [S31](src.s31.md)

If you're building an MCP server, you can allow individual tools to return results larger than the default persist-to-disk threshold of 50,000 characters by setting `_meta["anthropic/maxResultSizeChars"]` in the tool's `tools/list` response entry. Claude Code raises that tool's threshold to the annotated value, up to a hard ceiling of 500,000 characters.
