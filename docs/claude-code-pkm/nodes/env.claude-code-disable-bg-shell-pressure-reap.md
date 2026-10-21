---
id: env.claude-code-disable-bg-shell-pressure-reap
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP

**Sources:** [S81](src.s81.md)

Set to `1` to stop Claude Code from terminating background shell commands under memory pressure. By default, on macOS and Linux, Claude Code terminates background shells when the operating system reports critical memory pressure and the session has been idle for 30 minutes with no turn or subagent running. Windows has no memory-pressure signal, so this variable has no effect there. Requires Claude Code v2.1.193 or later
