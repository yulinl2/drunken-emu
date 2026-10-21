---
id: feature.previous-session-is-unavailable-run-remote-control-to-start
kind: feature
status: VERIFIED
title: "\"Previous session is unavailable — run /remote-control to start a new one\""
sources: [S21]
---

# "Previous session is unavailable — run /remote-control to start a new one"

**Sources:** [S21](src.s21.md)

Claude Code couldn't bring back the previous Remote Control session and stopped instead of starting a new one on its own. You can see this message after you resume a conversation with `claude --resume` or `claude --continue`, or after Claude Code reconnects on its own following a disconnect.
