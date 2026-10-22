---
id: feature.non-interactive-sessions
kind: feature
status: VERIFIED
title: "Non-interactive sessions"
sources: [S28]
---

# Non-interactive sessions

**Sources:** [S28](src.s28.md)

Claude Code binds an inbox socket for a `claude -p` session like an interactive one, so a long-running `-p` worker can receive messages and appears in the listing. When you start a session in bare mode, Claude Code doesn't bind the socket, so that session can't receive messages and doesn't appear in the agent list.
