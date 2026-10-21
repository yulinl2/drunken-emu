---
id: feature.reload-summary
kind: feature
status: VERIFIED
title: "Reload summary"
sources: [S52]
---

# Reload summary

**Sources:** [S52](src.s52.md)

Claude Code reloads every active plugin and prints one summary line, `Reloaded: N plugins · N skills · N agents · N hooks · N plugin MCP servers · N plugin LSP servers`, omitting the plugin MCP server count in a session without an interactive terminal. When any plugin failed, the summary adds `N errors during load. Run /plugin for details.`
