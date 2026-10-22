---
id: feature.at-mention-event
kind: feature
status: VERIFIED
title: "At mention event"
sources: [S65]
---

# At mention event

**Sources:** [S65](src.s65.md)

Logged when Claude Code resolves an `@`-mention in a prompt. Not every mention emits an event: early-exit paths such as permission denials, oversized files, PDF reference attachments, and directory listing failures return without logging.
