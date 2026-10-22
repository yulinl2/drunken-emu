---
id: feature.message-another-session
kind: feature
status: VERIFIED
title: "Message another session"
sources: [S28]
---

# Message another session

**Sources:** [S28](src.s28.md)

When one of your sessions learns something another session needs, such as a finding, a status, or a decision, Claude passes it along instead of you copy-pasting between terminals. Claude discovers the target with `ListAgents` and sends with `SendMessage`, so you never call either tool yourself. Claude can decide to send a message without being asked, and you can also prompt for one.
