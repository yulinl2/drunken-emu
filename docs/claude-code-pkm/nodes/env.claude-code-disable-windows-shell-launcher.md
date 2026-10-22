---
id: env.claude-code-disable-windows-shell-launcher
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_WINDOWS_SHELL_LAUNCHER"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_WINDOWS_SHELL_LAUNCHER

**Sources:** [S81](src.s81.md)

Set to `1` to start PowerShell tool commands on Windows directly instead of through the `cmd.exe` launcher. By default, the launcher lets a PowerShell command running in the background carry over to the session's next process, such as when you background the session. If you set the variable, a backgrounded PowerShell command stops when the session's process exits. Bash commands aren't affected. Requires Claude Code v2.1.269 or later
