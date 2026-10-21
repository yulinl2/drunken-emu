---
id: feature.disable-session-scoped-scheduled-tasks
kind: feature
status: VERIFIED
title: "Disable session-scoped scheduled tasks"
sources: [S36]
---

# Disable session-scoped scheduled tasks

**Sources:** [S36](src.s36.md)

Set `CLAUDE_CODE_DISABLE_CRON=1` in your environment to disable the scheduler entirely. The cron tools and `/loop` become unavailable, and any already-scheduled tasks stop firing. See Environment variables for the full list of disable flags.
