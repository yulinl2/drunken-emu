---
id: feature.reloads-that-change-mcp-tools
kind: feature
status: VERIFIED
title: "Reloads that change MCP tools"
sources: [S52]
---

# Reloads that change MCP tools

**Sources:** [S52](src.s52.md)

When the reload would add or remove a plugin MCP server or the `LSP` tool, and that change would invalidate the prompt cache, Claude Code doesn't apply the reload. It prints a line such as `This reload changes MCP tools () — your next message will re-read the whole conversation instead of using the cache. Run /reload-plugins --force to apply.` Pass `--force` to apply it anyway.
