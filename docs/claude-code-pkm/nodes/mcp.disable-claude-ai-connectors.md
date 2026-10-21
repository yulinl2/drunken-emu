---
id: mcp.disable-claude-ai-connectors
kind: mcp
status: VERIFIED
title: "Disable claude.ai connectors"
sources: [S31]
---

# Disable claude.ai connectors

**Sources:** [S31](src.s31.md)

Claude Code applies `disableClaudeAiConnectors` only to the connectors it fetches itself, not to the connectors a cloud host or the desktop app delivers. To turn off the connectors it fetches, set the setting to `true` in any settings scope:
