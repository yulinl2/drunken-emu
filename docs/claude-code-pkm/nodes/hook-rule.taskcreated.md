---
id: hook-rule.taskcreated
kind: hook-rule
status: VERIFIED
title: "TaskCreated"
sources: [S85]
---

# TaskCreated

**Sources:** [S85](src.s85.md)

Runs when a task is being created via the `TaskCreate` tool. Use this to enforce naming conventions, require task descriptions, or prevent certain tasks from being created. In a session without the Task tools, this event doesn't fire.
