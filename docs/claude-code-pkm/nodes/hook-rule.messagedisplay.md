---
id: hook-rule.messagedisplay
kind: hook-rule
status: VERIFIED
title: "MessageDisplay"
sources: [S85]
---

# MessageDisplay

**Sources:** [S85](src.s85.md)

Runs while an assistant message streams to the screen. Claude Code displays the message in increments: each time a batch of newly completed lines is ready to render, the hook runs once with those lines and Claude Code renders the hook's replacement text in their place. A long message produces several calls; a short message may produce only one.
