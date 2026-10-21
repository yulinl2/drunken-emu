---
id: mod.rewrite-an-event
kind: mod
status: VERIFIED
title: "Rewrite an event"
sources: [S55]
---

# Rewrite an event

**Sources:** [S55](src.s55.md)

To change what Claude Code acts on, such as the text of a prompt, call `next` with a modified copy of the event. The event itself is immutable: it's deeply frozen, and assigning to a field throws. This hook trims each prompt before it's sent:
