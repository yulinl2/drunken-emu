---
id: mod.stop-background-work
kind: mod
status: VERIFIED
title: "Stop background work"
sources: [S56]
---

# Stop background work

**Sources:** [S56](src.s56.md)

Timers stop when the module reloads. For long-running work inside a hook, `next.signal` is an `AbortSignal` that aborts when the event your hook is handling is abandoned, for example when the user interrupts, so pass it to anything long-running.
