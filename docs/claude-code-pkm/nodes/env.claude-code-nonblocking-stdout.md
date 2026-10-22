---
id: env.claude-code-nonblocking-stdout
kind: env
status: VERIFIED
title: "CLAUDE_CODE_NONBLOCKING_STDOUT"
sources: [S81]
---

# CLAUDE_CODE_NONBLOCKING_STDOUT

**Sources:** [S81](src.s81.md)

Set to `1` to write terminal output through a second non-blocking file descriptor, so a terminal that stops reading, such as a paused tmux control-mode pane or a stalled SSH connection, can't freeze Claude Code mid-session. Applies on macOS, Linux, and WSL when stdout is a terminal. Requires Claude Code v2.1.261 or later
