---
id: mcp.allow-claude-ai-connectors-alongside-the-managed-set
kind: mcp
status: VERIFIED
title: "Allow claude.ai connectors alongside the managed set"
sources: [S63]
---

# Allow claude.ai connectors alongside the managed set

**Sources:** [S63](src.s63.md)

By default, deploying `managed-mcp.json` suppresses the claude.ai connectors Claude Code fetches itself, including connectors an administrator configured for the organization in the claude.ai admin console. To load those connectors alongside the servers in `managed-mcp.json`, set `"allowAllClaudeAiMcps": true` in a managed settings source.
