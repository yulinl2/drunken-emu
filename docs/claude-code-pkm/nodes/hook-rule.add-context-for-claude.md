---
id: hook-rule.add-context-for-claude
kind: hook-rule
status: VERIFIED
title: "Add context for Claude"
sources: [S85]
---

# Add context for Claude

**Sources:** [S85](src.s85.md)

The `additionalContext` field passes a string from your hook into Claude's context window. Claude Code wraps the string in a system reminder and inserts it into the conversation at the point where the hook fired. Claude reads the reminder on the next model request, but it doesn't appear as a chat message in the interface.
