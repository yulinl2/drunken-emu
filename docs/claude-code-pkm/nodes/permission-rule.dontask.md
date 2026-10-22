---
id: permission-rule.dontask
kind: permission-rule
status: VERIFIED
title: "dontAsk"
sources: [S66]
---

# dontAsk

**Sources:** [S66](src.s66.md)

Auto-denies every call that would otherwise prompt, though a mod you installed can still approve some of those calls. File reads in your working directories and other actions that need no approval still run, as do tools pre-approved via `/permissions` or `permissions.allow` rules. `AskUserQuestion`, MCP tools marked `requiresUserInteraction`, reads from network paths, and connector tools your organization set to `ask` in sessions where that setting reaches Claude Code are denied even if you've allowed them
