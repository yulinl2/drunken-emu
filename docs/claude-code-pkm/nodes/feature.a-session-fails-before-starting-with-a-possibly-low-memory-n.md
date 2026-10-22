---
id: feature.a-session-fails-before-starting-with-a-possibly-low-memory-n
kind: feature
status: VERIFIED
title: "A session fails before starting with a possibly low memory note"
sources: [S26]
---

# A session fails before starting with a possibly low memory note

**Sources:** [S26](src.s26.md)

When a background session's process exits before it finishes starting and the host is low on memory, the row's status names the exit and adds `possibly low memory — free some up and retry`.
