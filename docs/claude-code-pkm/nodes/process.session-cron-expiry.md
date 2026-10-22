---
id: process.session-cron-expiry
kind: process
status: VERIFIED
title: "Session cron expiry"
sources: [S7]
---

# Session cron expiry

**Sources:** [S7](src.s7.md)

Recurring session-scoped jobs expire after 7 days: they fire one last time, then are deleted. A recurring job can run up to half its period late, at most 30 minutes. See [CronCreate](tool.cron-create.md).
