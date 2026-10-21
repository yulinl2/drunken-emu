---
id: feature.enable-remote-control-for-all-sessions
kind: feature
status: VERIFIED
title: "Enable Remote Control for all sessions"
sources: [S21]
---

# Enable Remote Control for all sessions

**Sources:** [S21](src.s21.md)

Remote Control only activates when you explicitly run `claude remote-control`, `claude --remote-control`, or `/remote-control`, unless auto-connect is turned on. To turn auto-connect on for every interactive session, run `/config` inside Claude Code and set Enable Remote Control for all sessions. The toggle takes three values:
