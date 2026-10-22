---
id: feature.how-background-sessions-are-hosted
kind: feature
status: VERIFIED
title: "How background sessions are hosted"
sources: [S26]
---

# How background sessions are hosted

**Sources:** [S26](src.s26.md)

Claude Code treats every session listed in agent view as a background session, whether or not you're currently attached to it. By contrast, a session started by running `claude` directly is tied to that terminal and ends when it closes, unless you send it to the background.
