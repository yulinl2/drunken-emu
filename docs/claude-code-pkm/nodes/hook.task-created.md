---
id: hook.task-created
kind: hook
status: VERIFIED
title: "TaskCreated"
sources: [S2]
---

# TaskCreated

**Sources:** [S2](src.s2.md)

Fires when a task is created with TaskCreate ([TaskCreate](tool.task-create.md)). No matcher. Exit 2 rolls the task back. A top-level decision block cancels it.
