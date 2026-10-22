---
id: agent-field.dontask
kind: agent-field
status: VERIFIED
title: "dontAsk"
sources: [S25]
---

# dontAsk

**Sources:** [S25](src.s25.md)

Auto-denies calls that would prompt, though a mod you installed can still approve some of those calls. Explicitly allowed tools still work. `AskUserQuestion`, MCP tools marked `requiresUserInteraction`, reads from network paths, and connector tools your organization set to `ask` in sessions where that setting reaches Claude Code are denied even if you've allowed them
