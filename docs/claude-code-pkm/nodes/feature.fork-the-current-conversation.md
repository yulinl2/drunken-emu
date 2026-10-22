---
id: feature.fork-the-current-conversation
kind: feature
status: VERIFIED
title: "Fork the current conversation"
sources: [S25]
---

# Fork the current conversation

**Sources:** [S25](src.s25.md)

A fork is a subagent that inherits the entire conversation so far instead of starting fresh. This drops the input isolation that subagents otherwise provide: a fork sees the same system prompt, tools, model, and message history as the main session, so you can hand it a side task without re-explaining the situation. The fork's own tool calls still stay out of your conversation and only its final re
