---
id: tool.memory-limit-on-linux-and-wsl
kind: tool
status: VERIFIED
title: "Memory limit on Linux and WSL"
sources: [S82]
---

# Memory limit on Linux and WSL

**Sources:** [S82](src.s82.md)

On Linux and WSL, set `CLAUDE_CODE_TOOL_MEMORY_LIMIT` to a size such as `4G` to cap the memory that Bash, PowerShell, and Monitor tool commands can use, so one runaway build can't take the memory the rest of the session needs. Requires Claude Code v2.1.233 or later. Before v2.1.246, Monitor tool commands ran outside the cap.
