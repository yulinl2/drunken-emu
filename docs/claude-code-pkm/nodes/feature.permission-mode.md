---
id: feature.permission-mode
kind: feature
status: VERIFIED
title: "Permission mode"
sources: [S26]
---

# Permission mode

**Sources:** [S26](src.s26.md)

Backgrounded with `/bg` or `←`: Claude Code keeps the permission mode the session was in, so one you switched to `acceptEdits` or `auto` stays there after detaching Dispatched from `claude agents` started in a shell, or with `claude --bg`: the new session starts the way a new `claude` session in that directory would, unless you dispatched it from an agent view you opened with dispatch defaults. Wh
