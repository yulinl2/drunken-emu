---
id: hook-rule.taskcompleted
kind: hook-rule
status: VERIFIED
title: "TaskCompleted"
sources: [S85]
---

# TaskCompleted

**Sources:** [S85](src.s85.md)

Runs when a task is being marked as completed. This fires in two situations: when any agent explicitly marks a task as completed through the TaskUpdate tool, or when an agent team teammate finishes its turn with in-progress tasks. Use this to enforce completion criteria like passing tests or lint checks before a task can close.
