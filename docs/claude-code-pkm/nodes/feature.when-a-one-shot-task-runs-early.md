---
id: feature.when-a-one-shot-task-runs-early
kind: feature
status: VERIFIED
title: "When a one-shot task runs early"
sources: [S36]
---

# When a one-shot task runs early

**Sources:** [S36](src.s36.md)

A one-shot task scheduled for `:00` or `:30` runs up to 90 seconds early. Claude Code doesn't shift a one-shot task scheduled for any other minute, so when the timing matters, schedule it off the hour and half hour: `3 9 * * *` instead of `0 9 * * *`.
