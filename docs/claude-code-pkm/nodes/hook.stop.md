---
id: hook.stop
kind: hook
status: VERIFIED
title: "Stop"
sources: [S2]
---

# Stop

**Sources:** [S2](src.s2.md)

Fires when Claude finishes responding. No matcher. Exit 2 blocks, so Claude keeps working. Top-level decision block applies. Input: [Stdin: Stop and SubagentStop fields](hook-rule.stdin-stop.md).

## Linked from

- [Observation: user-level Stop hook reached the model](obs.user-stop-hook-feedback.md)
