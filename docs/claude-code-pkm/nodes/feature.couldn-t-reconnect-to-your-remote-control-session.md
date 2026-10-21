---
id: feature.couldn-t-reconnect-to-your-remote-control-session
kind: feature
status: VERIFIED
title: "\"Couldn't reconnect to your Remote Control session\""
sources: [S21]
---

# "Couldn't reconnect to your Remote Control session"

**Sources:** [S21](src.s21.md)

When you resume a conversation with `claude --resume` or `claude --continue`, Claude Code reconnects to the Remote Control session recorded in that conversation. This message means the reconnection failed for a reason that may be temporary, such as a network interruption or a server error, so Claude Code can't confirm whether the remote session still exists.
