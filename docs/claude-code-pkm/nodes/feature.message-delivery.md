---
id: feature.message-delivery
kind: feature
status: VERIFIED
title: "Message delivery"
sources: [S28]
---

# Message delivery

**Sources:** [S28](src.s28.md)

The receiving Claude reads the message between tool calls during an active turn, so a running tool is never interrupted. When the receiving session is idle, Claude Code starts a new turn with the message.
