---
id: env.claude-code-worker-checkin-schedule
kind: env
status: VERIFIED
title: "CLAUDE_CODE_WORKER_CHECKIN_SCHEDULE"
sources: [S81]
---

# CLAUDE_CODE_WORKER_CHECKIN_SCHEDULE

**Sources:** [S81](src.s81.md)

When `CLAUDE_AUTO_BACKGROUND_TASKS` is set to `1`, how long Claude Code waits before each reminder to Claude to check on background subagents that are still running. Takes one or more comma-separated waits in whole seconds from `1` to `86400`, such as `600` or `600,1800,3600`. Each value is the wait before the next reminder, and the last value repeats. Takes plain digits only; any other value or spelling reads as unset. When unset, there are no reminders. Requires Claude Code v2.1.283 or later
