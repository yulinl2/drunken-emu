---
id: tool.when-a-background-command-stops
kind: tool
status: VERIFIED
title: "When a background command stops"
sources: [S82]
---

# When a background command stops

**Sources:** [S82](src.s82.md)

A command that a foreground subagent started stops when that subagent's run ends, whether it finished, failed, or was interrupted. A command that the main conversation or a background subagent started keeps running after a final response, until it exits, is stopped, or reaches its time limit.
