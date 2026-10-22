---
id: feature.the-terminal-host-died-or-the-session-stopped-responding
kind: feature
status: VERIFIED
title: "The terminal host died or the session stopped responding"
sources: [S26]
---

# The terminal host died or the session stopped responding

**Sources:** [S26](src.s26.md)

The supervisor runs each background session's terminal in its own host process. When that process dies or stops responding, Claude Code shows the reason and offers a restart; in both cases the conversation is saved and the restart resumes it. The error reference quotes the full messages.
