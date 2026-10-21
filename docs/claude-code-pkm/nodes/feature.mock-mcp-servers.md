---
id: feature.mock-mcp-servers
kind: feature
status: VERIFIED
title: "Mock MCP servers"
sources: [S47]
---

# Mock MCP servers

**Sources:** [S47](src.s47.md)

You can evaluate a plugin whose skills call MCP tools without the real service behind them. Put one Markdown file per tool under `evals/mocks//.md` for the whole suite, or under a case's own `mocks/` directory for one case, where `` is the server's name in your plugin's MCP configuration.
