---
id: feature.what-loads-at-startup
kind: feature
status: VERIFIED
title: "What loads at startup"
sources: [S25]
---

# What loads at startup

**Sources:** [S25](src.s25.md)

Each subagent starts with a fresh, isolated context window. It doesn't see your conversation history, the skills you've already invoked, or the files Claude has already read. Claude composes a delegation message that summarizes the task, and the subagent works from there. The exception is a fork, which inherits the parent conversation instead of starting fresh.
