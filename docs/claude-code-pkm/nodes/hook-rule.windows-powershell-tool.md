---
id: hook-rule.windows-powershell-tool
kind: hook-rule
status: VERIFIED
title: "Windows PowerShell tool"
sources: [S85]
---

# Windows PowerShell tool

**Sources:** [S85](src.s85.md)

On Windows, you can run individual hooks in PowerShell by setting `"shell": "powershell"` on a command hook. Claude Code auto-detects `pwsh.exe`, the PowerShell 7 and later executable, and falls back to `powershell.exe` for Windows PowerShell 5.1.
