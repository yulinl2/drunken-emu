---
id: feature.how-session-scoped-scheduled-tasks-run
kind: feature
status: VERIFIED
title: "How session-scoped scheduled tasks run"
sources: [S36]
---

# How session-scoped scheduled tasks run

**Sources:** [S36](src.s36.md)

The scheduler checks every second for due tasks and enqueues them at low priority. A scheduled prompt fires between your turns, not while Claude is mid-response. If Claude is busy when a task comes due, the prompt waits until the current turn ends.
