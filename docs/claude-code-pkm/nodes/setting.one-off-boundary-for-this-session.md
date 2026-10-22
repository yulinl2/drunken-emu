---
id: setting.one-off-boundary-for-this-session
kind: setting
status: VERIFIED
title: "One-off boundary for this session"
sources: [S64]
---

# One-off boundary for this session

**Sources:** [S64](src.s64.md)

The classifier blocks matching actions, but the boundary can be lost if context compaction removes the message that stated it. Use an ask or deny rule for a durable guarantee. (mechanism: State it in conversation, like "don't push until I review")
