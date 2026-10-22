---
id: feature.trust-required-for-inline-mcp-servers
kind: feature
status: VERIFIED
title: "Trust required for inline MCP servers"
sources: [S25]
---

# Trust required for inline MCP servers

**Sources:** [S25](src.s25.md)

Claude Code loads an inline MCP server from an agent file in your project's `.claude/agents/` directory, or in an `--add-dir` directory's `.claude/agents/`, only after you trust the folder the agent file came from. Before v2.1.238, Claude Code loaded these servers without checking trust.
