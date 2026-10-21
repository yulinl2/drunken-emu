---
id: feature.queue-messages-while-claude-works
kind: feature
status: VERIFIED
title: "Queue messages while Claude works"
sources: [S83]
---

# Queue messages while Claude works

**Sources:** [S83](src.s83.md)

Type a message and press `Enter` while Claude is working. Claude Code queues the message instead of interrupting the turn, and lists the queued entries in the conversation until it sends them. You can queue `!` shell commands and most commands the same way, apart from the commands, such as `/status`, that Claude Code runs as soon as you send them.
