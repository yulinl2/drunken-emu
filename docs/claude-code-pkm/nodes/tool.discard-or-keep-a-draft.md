---
id: tool.discard-or-keep-a-draft
kind: tool
status: VERIFIED
title: "Discard or keep a draft"
sources: [S82]
---

# Discard or keep a draft

**Sources:** [S82](src.s82.md)

When you discard a draft, Claude Code deletes it from your machine. A draft you leave in the queue expires after 30 days, or after `cleanupPeriodDays` when that's shorter. The queue holds 10 drafts across all your sessions, and when Claude queues an eleventh, Claude Code deletes the oldest. When you run `/exit` with drafts from the session still in the queue, Claude Code asks whether to review the
