---
id: env.claude-code-messaging-socket
kind: env
status: VERIFIED
title: "CLAUDE_CODE_MESSAGING_SOCKET"
sources: [S81]
---

# CLAUDE_CODE_MESSAGING_SOCKET

**Sources:** [S81](src.s81.md)

Set by Claude Code, not by you: in sessions that bind an inbox socket, Claude Code exports that socket's path to hooks and Bash commands when it binds the socket. In a session that starts with messaging on, Claude Code binds the socket before any hook runs. Other sessions on the machine deliver messages to this path. Each session exports its own socket rather than one inherited from a parent, and messages arriving on it go through the session's inbound controls. Settings `env` blocks can't set it. Requires Claude Code v2.1.224 or later
