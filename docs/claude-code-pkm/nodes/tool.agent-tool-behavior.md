---
id: tool.agent-tool-behavior
kind: tool
status: VERIFIED
title: "Agent tool behavior"
sources: [S82]
---

# Agent tool behavior

**Sources:** [S82](src.s82.md)

The Agent tool spawns a subagent in a separate context window. The subagent works through its task autonomously, then returns its result to the parent conversation. The parent doesn't see the subagent's intermediate tool calls or outputs, only that final result. The same tool can also launch a teammate or a fork:
