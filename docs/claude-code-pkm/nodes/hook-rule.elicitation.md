---
id: hook-rule.elicitation
kind: hook-rule
status: VERIFIED
title: "Elicitation"
sources: [S85]
---

# Elicitation

**Sources:** [S85](src.s85.md)

Runs when an MCP server requests user input mid-task. By default, Claude Code shows an interactive dialog for the user to respond. Hooks can intercept this request and respond programmatically, skipping the dialog entirely.
