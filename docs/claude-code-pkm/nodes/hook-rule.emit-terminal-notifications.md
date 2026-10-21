---
id: hook-rule.emit-terminal-notifications
kind: hook-rule
status: VERIFIED
title: "Emit terminal notifications"
sources: [S85]
---

# Emit terminal notifications

**Sources:** [S85](src.s85.md)

Hooks run without a controlling terminal, so writing escape sequences directly to `/dev/tty` fails. Instead, return the escape sequence in the `terminalSequence` field and Claude Code emits it for you through its own terminal write path. This is race-free, works inside tmux and GNU screen, and works on Windows where there is no `/dev/tty`.
