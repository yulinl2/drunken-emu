---
id: feature.compacting-the-conversation
kind: feature
status: VERIFIED
title: "Compacting the conversation"
sources: [S18]
---

# Compacting the conversation

**Sources:** [S18](src.s18.md)

Compaction replaces your message history with a summary. By design, this invalidates the conversation layer: the next request has a new, shorter history that doesn't share a prefix with the old one. The system prompt and project context layers can stay cached:
