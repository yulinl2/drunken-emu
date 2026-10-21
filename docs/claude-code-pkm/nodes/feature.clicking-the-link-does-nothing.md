---
id: feature.clicking-the-link-does-nothing
kind: feature
status: VERIFIED
title: "Clicking the link does nothing"
sources: [S39]
---

# Clicking the link does nothing

**Sources:** [S39](src.s39.md)

The handler likely isn't registered yet. Registration happens when you send your first prompt of an interactive session, not when the session starts. Start an interactive `claude` session on that machine, send any prompt, exit, and try the link again. If you are on Linux without a desktop environment, `xdg-open` may have nothing to dispatch to.
