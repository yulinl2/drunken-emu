---
id: env.claude-pid
kind: env
status: VERIFIED
title: "CLAUDE_PID"
sources: [S81]
---

# CLAUDE_PID

**Sources:** [S81](src.s81.md)

Claude Code sets this to its own process ID in the subprocesses it spawns: Bash and PowerShell tool commands and hook commands. On Linux, the Bash tool's shell integration uses it to refuse a `pkill` pattern that would match the Claude Code process itself; see the error reference. Read it from your own scripts to identify or signal the parent Claude Code process deliberately. Requires Claude Code v2.1.214 or later
