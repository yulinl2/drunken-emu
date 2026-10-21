---
id: feature.what-survives-compaction
kind: feature
status: VERIFIED
title: "What survives compaction"
sources: [S17]
---

# What survives compaction

**Sources:** [S17](src.s17.md)

When a long session compacts, Claude Code summarizes the conversation history to fit the context window. As of v2.1.198, the summarization request inherits your session's extended thinking configuration, so it reasons with thinking enabled when your session has it enabled and stays off otherwise. Thinking affects only how the summary is produced; your session settings are unchanged afterward. What
