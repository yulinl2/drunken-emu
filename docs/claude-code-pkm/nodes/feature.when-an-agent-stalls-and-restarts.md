---
id: feature.when-an-agent-stalls-and-restarts
kind: feature
status: VERIFIED
title: "When an agent stalls and restarts"
sources: [S29]
---

# When an agent stalls and restarts

**Sources:** [S29](src.s29.md)

An agent whose output stops arriving for long enough starts over from the same prompt. In `/workflows`, its name gains a `(retry 1)` suffix and its detail shows `attempt 2 (stalled)`. The restart is automatic, so you don't need to do anything.
