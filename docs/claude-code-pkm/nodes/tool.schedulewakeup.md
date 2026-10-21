---
id: tool.schedulewakeup
kind: tool
status: VERIFIED
title: "ScheduleWakeup"
sources: [S82]
---

# ScheduleWakeup

**Sources:** [S82](src.s82.md)

Reschedules the next iteration of a self-paced `/loop`. Claude calls this at the end of each iteration to pick when the next one runs, between one minute and one hour out; you don't call it directly. To end the loop instead, Claude calls it with `stop: true`, which cancels the pending wakeup. The pending wakeup appears in `session_crons` in Stop hook input (permission required: No)
