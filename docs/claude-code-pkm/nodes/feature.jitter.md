---
id: feature.jitter
kind: feature
status: VERIFIED
title: "Jitter"
sources: [S36]
---

# Jitter

**Sources:** [S36](src.s36.md)

A scheduled task can run at a different time than its schedule says. If every session's tasks ran exactly on schedule, many of them would call the API at the same moment, so Claude Code shifts each task's run time. Recurring tasks run late, except a task that runs every five minutes, written `*/5 * * * *`. One-shot tasks scheduled on the hour or half hour run a little early.
