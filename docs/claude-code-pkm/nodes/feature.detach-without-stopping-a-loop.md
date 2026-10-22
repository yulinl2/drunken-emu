---
id: feature.detach-without-stopping-a-loop
kind: feature
status: VERIFIED
title: "Detach without stopping a loop"
sources: [S36]
---

# Detach without stopping a loop

**Sources:** [S36](src.s36.md)

When you're attached to a background session and Claude is idle, press `Ctrl+C` twice on an empty prompt to detach. A self-paced loop waiting there for its next iteration keeps running, and that iteration starts on schedule. To stop the loop instead, press `Esc` before you detach. Detaching with `Ctrl+C` without stopping the loop requires Claude Code v2.1.295 or later.
