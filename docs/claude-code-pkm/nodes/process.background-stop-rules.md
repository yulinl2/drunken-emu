---
id: process.background-stop-rules
kind: process
status: VERIFIED
title: "When a background command stops"
sources: [S6]
---

# When a background command stops

**Sources:** [S6](src.s6.md)

A command started by a foreground subagent stops when that subagent's run ends. A command started by the main conversation, or by a background subagent, runs until it exits, is stopped, or reaches its limit. A -p run stays open until its command ends.
