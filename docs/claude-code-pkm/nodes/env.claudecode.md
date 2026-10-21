---
id: env.claudecode
kind: env
status: VERIFIED
title: "CLAUDECODE"
sources: [S81]
---

# CLAUDECODE

**Sources:** [S81](src.s81.md)

Set to `1` in subprocesses Claude Code spawns (Bash and PowerShell tools, tmux sessions, hook commands, status line commands, stdio MCP server subprocesses). IDE extensions also set this in their integrated terminals. Use to detect when a script is running inside a subprocess spawned by Claude Code. To check whether the current process was spawned directly by a tool call or hook, rather than inside a stdio MCP server that Claude Code started, use `CLAUDE_CODE_CHILD_SESSION` instead
