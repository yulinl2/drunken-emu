---
id: feature.messages-between-agents
kind: feature
status: VERIFIED
title: "Messages between agents"
sources: [S27]
---

# Messages between agents

**Sources:** [S27](src.s27.md)

When one agent sends another a message over `SendMessage`, Claude Code tells the receiving agent the message came from another Claude session, not from you. A teammate can't approve a permission prompt or supply consent on your behalf, and a teammate that was denied an action can't relay it to another teammate to bypass the check. The same rules apply to a message that arrives from one of your oth
