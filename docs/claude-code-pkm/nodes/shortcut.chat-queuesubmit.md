---
id: shortcut.chat-queuesubmit
kind: shortcut
status: VERIFIED
title: "chat:queueSubmit"
sources: [S79]
---

# chat:queueSubmit

**Sources:** [S79](src.s79.md)

Submit the message, marked to wait its turn: while Claude is working, Claude Code queues it and never interrupts the turn. Unlike `chat:submit`, it submits the draft even while an autocomplete suggestion is highlighted. Requires v2.1.247 or later (default: Ctrl+X Enter)
