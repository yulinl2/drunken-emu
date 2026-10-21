---
id: mod.redraw-on-a-timer
kind: mod
status: VERIFIED
title: "Redraw on a timer"
sources: [S57]
---

# Redraw on a timer

**Sources:** [S57](src.s57.md)

To keep a clock, a countdown, or a value from outside the session current, redraw on a schedule. Start a timer in the module's `session.start` hook. If the module already has one, as `hello-tabs` does, add the `$.clock.every` line to it:
