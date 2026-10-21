---
id: feature.hook-registered-event
kind: feature
status: VERIFIED
title: "Hook registered event"
sources: [S65]
---

# Hook registered event

**Sources:** [S65](src.s65.md)

Logged once per configured hook at session start. Use this event to inventory which hooks are active across your fleet, as a complement to the per-execution `hook_execution_start` and `hook_execution_complete` events.
