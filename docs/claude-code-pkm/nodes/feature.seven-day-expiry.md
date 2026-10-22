---
id: feature.seven-day-expiry
kind: feature
status: VERIFIED
title: "Seven-day expiry"
sources: [S36]
---

# Seven-day expiry

**Sources:** [S36](src.s36.md)

Recurring tasks automatically expire 7 days after creation. The task fires one final time, then deletes itself. This bounds how long a forgotten loop can run. If you need a recurring task to last longer, cancel and recreate it before it expires, or use cloud scheduled tasks or Desktop scheduled tasks for durable scheduling.
