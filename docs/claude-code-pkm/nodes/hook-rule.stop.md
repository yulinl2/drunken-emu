---
id: hook-rule.stop
kind: hook-rule
status: VERIFIED
title: "Stop"
sources: [S85]
---

# Stop

**Sources:** [S85](src.s85.md)

Runs when the main Claude Code agent has finished responding. Does not run if the stoppage occurred due to a user interrupt. API errors fire StopFailure instead.
