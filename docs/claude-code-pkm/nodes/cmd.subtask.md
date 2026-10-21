---
id: cmd.subtask
kind: command
status: VERIFIED
title: "/subtask"
sources: [S80]
---

# /subtask

**Sources:** [S80](src.s80.md)

Spawn a forked subagent: a background subagent that inherits the full conversation and works on the task while you keep working. Its result returns to this conversation when it finishes. To copy the conversation into a separate background session instead, use `/fork`. When agent view is turned off, `/subtask` isn't available and `/fork` spawns the forked subagent instead
