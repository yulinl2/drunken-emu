---
id: hook-field.terminalsequence
kind: hook-field
status: VERIFIED
title: "terminalSequence"
sources: [S85]
---

# terminalSequence

**Sources:** [S85](src.s85.md)

A terminal escape sequence for Claude Code to emit on your behalf, such as a desktop notification, window title, or bell. Restricted to OSC `0`/`1`/`2`/`9`/`99`/`777` and BEL. If the value contains anything outside the allowlist, the field is ignored. Use this instead of writing to `/dev/tty`, which is unavailable to hooks (default: none)
