---
id: hook-rule.quota-auto-resume-disabled
kind: hook-rule
status: VERIFIED
title: "quota_auto_resume_disabled"
sources: [S85]
---

# quota_auto_resume_disabled

**Sources:** [S85](src.s85.md)

when it fires: Claude Code ends its wait for a claude.ai usage limit without continuing your task: `autoContinueAtUsageLimit` turned off or the reset moved more than 24 hours away during a wait Claude Code started on its own, the continued task kept hitting the limit, or the continuation was blocked before it reached the model. Doesn't fire when you press `Esc` or `Ctrl+C`, or pick Don't continue automatically
