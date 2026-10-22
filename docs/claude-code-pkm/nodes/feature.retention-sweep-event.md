---
id: feature.retention-sweep-event
kind: feature
status: VERIFIED
title: "Retention sweep event"
sources: [S65]
---

# Retention sweep event

**Sources:** [S65](src.s65.md)

Logged once per run of the retention cleanup sweep, which deletes session transcripts and other application data older than the `cleanupPeriodDays` setting. Claude Code runs the sweep in the background at most once per session, and a run that deletes nothing still emits the event. If Claude Code ran the sweep in any session on the same machine in the last 24 hours, it delays this session's sweep b
