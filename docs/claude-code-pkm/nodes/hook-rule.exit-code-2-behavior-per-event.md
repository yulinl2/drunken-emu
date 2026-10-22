---
id: hook-rule.exit-code-2-behavior-per-event
kind: hook-rule
status: VERIFIED
title: "Exit code 2 behavior per event"
sources: [S85]
---

# Exit code 2 behavior per event

**Sources:** [S85](src.s85.md)

Exit code 2 is the way a hook signals "stop, don't do this." The effect depends on the event, because some events represent actions that can be blocked (like a tool call that hasn't happened yet) and others represent things that already happened or can't be prevented.
