---
id: hook-rule.quota-auto-resume-stale
kind: hook-rule
status: VERIFIED
title: "quota_auto_resume_stale"
sources: [S85]
---

# quota_auto_resume_stale

**Sources:** [S85](src.s85.md)

when it fires: A claude.ai usage limit reset while your computer slept for more than about 30 minutes. Claude Code waits for you to press `Enter` instead of continuing. After a shorter sleep it continues and fires `quota_auto_resume_fired` instead
