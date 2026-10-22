---
id: env.claude-code-disable-cron
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_CRON"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_CRON

**Sources:** [S81](src.s81.md)

Set to `1` to disable session-scoped scheduled tasks. The `/loop` skill and cron tools become unavailable and any already-scheduled tasks stop firing, including tasks that are already running mid-session
