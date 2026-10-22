---
id: question.q6
kind: question
status: OPEN
title: "Q6 (doubt): Which maximum applies to Monitor deadlines?"
sources: [S6, S7]
---

# Q6 (doubt): Which maximum applies to Monitor deadlines?

**Sources:** [S6](src.s6.md), [S7](src.s7.md)

The schema of [Monitor](tool.monitor.md) allows timeout_ms up to 3,600,000 ms, but its own description says deadlines above 1,800,000 ms are capped. The tools reference says at most 30 minutes. Next check: treat 30 minutes as the cap, and test one long watch.

## Linked from

- [Monitor](tool.monitor.md)
- [Monitor deadline](process.monitor-deadline.md)
