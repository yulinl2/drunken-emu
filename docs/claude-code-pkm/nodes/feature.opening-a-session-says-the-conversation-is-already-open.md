---
id: feature.opening-a-session-says-the-conversation-is-already-open
kind: feature
status: VERIFIED
title: "Opening a session says the conversation is already open"
sources: [S26]
---

# Opening a session says the conversation is already open

**Sources:** [S26](src.s26.md)

Two processes can't write to the same transcript. When a stopped session's saved conversation is already open in another live Claude Code process, Claude Code refuses to start the session's own process. What you see depends on what holds the conversation:
