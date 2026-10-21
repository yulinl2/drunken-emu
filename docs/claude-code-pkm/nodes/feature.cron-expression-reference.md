---
id: feature.cron-expression-reference
kind: feature
status: VERIFIED
title: "Cron expression reference"
sources: [S36]
---

# Cron expression reference

**Sources:** [S36](src.s36.md)

`CronCreate` accepts standard 5-field cron expressions: `minute hour day-of-month month day-of-week`. All fields support wildcards (`*`), single values (`5`), steps (`*/15`), ranges (`1-5`), and comma-separated lists (`1,15,30`).
