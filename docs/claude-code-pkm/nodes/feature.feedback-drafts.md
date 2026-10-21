---
id: feature.feedback-drafts
kind: feature
status: VERIFIED
title: "feedback/drafts/"
sources: [S16]
---

# feedback/drafts/

**Sources:** [S16](src.s16.md)

contents: Queued Claude-drafted feedback awaiting your review in `/feedback`. Swept after `cleanupPeriodDays` or 30 days, whichever is shorter. When the queue is at its 10-draft limit, Claude Code deletes the oldest draft to make room.
