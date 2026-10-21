---
id: process.loop-pacing
kind: process
status: VERIFIED
title: "Self-paced loop"
sources: [S6]
---

# Self-paced loop

**Sources:** [S6](src.s6.md)

A /loop can pace itself. At the end of each iteration Claude calls ScheduleWakeup for the next run, between 1 minute and 1 hour out. See [ScheduleWakeup](tool.schedule-wakeup.md).
