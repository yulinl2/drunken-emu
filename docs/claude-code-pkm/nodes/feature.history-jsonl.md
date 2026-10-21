---
id: feature.history-jsonl
kind: feature
status: VERIFIED
title: "history.jsonl"
sources: [S16]
---

# history.jsonl

**Sources:** [S16](src.s16.md)

contents: Prompts you've typed, with timestamp and project path. Used for up-arrow recall, `Ctrl+R` history search, and `!` shell-command completion. Each sweep removes the entries older than `cleanupPeriodDays` when the HIPAA configuration applies to your sessions.
