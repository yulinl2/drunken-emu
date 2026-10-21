---
id: env.claude-ax-startup-quiet-ms
kind: env
status: VERIFIED
title: "CLAUDE_AX_STARTUP_QUIET_MS"
sources: [S81]
---

# CLAUDE_AX_STARTUP_QUIET_MS

**Sources:** [S81](src.s81.md)

In screen reader mode, how many milliseconds Claude Code holds the first interface render after the startup confirmation line, so your screen reader can speak the line in full before new output interrupts it. Default `3000`. Set `0` to render immediately. Claude Code caps the hold at `600000` (10 minutes). Your first keystroke ends the hold early. Requires Claude Code v2.1.217 or later
