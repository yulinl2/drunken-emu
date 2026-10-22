---
id: mod.answer-an-event
kind: mod
status: VERIFIED
title: "Answer an event"
sources: [S55]
---

# Answer an event

**Sources:** [S55](src.s55.md)

To handle an event yourself, return a result without calling `next`. That short-circuits the chain, so later mods and Claude Code's own behavior don't run. This hook refuses every Bash command:
