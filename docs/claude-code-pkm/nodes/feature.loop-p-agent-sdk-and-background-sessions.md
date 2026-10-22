---
id: feature.loop-p-agent-sdk-and-background-sessions
kind: feature
status: VERIFIED
title: "/loop, -p, Agent SDK, and background sessions"
sources: [S20]
---

# /loop, -p, Agent SDK, and background sessions

**Sources:** [S20](src.s20.md)

Sessions whose first prompt was a `/loop` command don't appear in the picker, and `claude --continue` skips them too. Running `/loop` later in a conversation doesn't hide the session.
