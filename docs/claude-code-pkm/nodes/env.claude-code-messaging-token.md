---
id: env.claude-code-messaging-token
kind: env
status: VERIFIED
title: "CLAUDE_CODE_MESSAGING_TOKEN"
sources: [S81]
---

# CLAUDE_CODE_MESSAGING_TOKEN

**Sources:** [S81](src.s81.md)

Set by Claude Code, not by you: in sessions that bind an inbox socket, Claude Code exports this per-session token to hooks and Bash commands alongside `CLAUDE_CODE_MESSAGING_SOCKET`. A script posting to the socket can send `{"type":"auth","token":""}` as its first line to prove it belongs to the session. On native Windows, Claude Code requires this line and closes any connection that doesn't open with a valid one. The own-child rules say when Claude Code consults the token. Each session exports its own token, never one inherited from a parent session. Settings `env` blocks can't set it. Requires Claude Code v2.1.228 or later
