---
id: cmd.bug
kind: command
status: VERIFIED
title: "/bug"
sources: [S80]
---

# /bug

**Sources:** [S80](src.s80.md)

Report a bug or share your conversation. You choose how much session history to include and confirm on a consent screen before anything is sent. When you're signed in to Anthropic on a first-party connection, the report goes to Anthropic; on a third-party provider, or without Anthropic credentials, Claude Code writes the report to a local archive under `~/.claude/feedback-bundles/` that you forward yourself. In the VS Code extension, `/bug` opens the extension's own feedback dialog instead; requires Claude Code v2.1.229 or later. When you run it while Claude is responding, Claude Code opens the dialog immediately. Before v2.1.232, Claude Code queued the command until the turn finished. Alias: `/share`. Before v2.1.212, `/bug` and `/share` were aliases of `/feedback`
