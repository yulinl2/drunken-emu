---
id: feature.what-deleting-a-session-removes
kind: feature
status: VERIFIED
title: "What deleting a session removes"
sources: [S26]
---

# What deleting a session removes

**Sources:** [S26](src.s26.md)

Delete a session with `Ctrl+X` twice in agent view or with `claude rm`. Except in the kept cases below, the session leaves the list. Its transcript stays on your machine through `claude --resume`, and the removal survives supervisor restarts.
