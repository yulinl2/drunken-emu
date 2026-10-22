---
id: feature.resume-or-fork-sessions
kind: feature
status: VERIFIED
title: "Resume or fork sessions"
sources: [S14]
---

# Resume or fork sessions

**Sources:** [S14](src.s14.md)

Resuming a session with `claude --continue` or `claude --resume` reopens it under the same session ID and appends new messages to the existing conversation. Forking with `--fork-session` or `/branch` copies the history into a new session ID, leaving the original unchanged.
