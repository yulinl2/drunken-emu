---
id: env.task-max-output-length
kind: env
status: VERIFIED
title: "TASK_MAX_OUTPUT_LENGTH"
sources: [S81]
---

# TASK_MAX_OUTPUT_LENGTH

**Sources:** [S81](src.s81.md)

Removed in v2.1.277 and now a no-op, together with the `TaskOutput` tool it sized. Previously set the maximum number of characters of a background task's output that the `TaskOutput` tool kept. Claude reads a background task's output file with `Read` instead
