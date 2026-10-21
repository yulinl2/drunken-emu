---
id: permission-mode.remove-item-in-powershell
kind: permission-mode
status: VERIFIED
title: "Remove-Item in PowerShell"
sources: [S67]
---

# Remove-Item in PowerShell

**Sources:** [S67](src.s67.md)

When you enable the PowerShell tool, Claude Code gives `Remove-Item` and the `cmd` built-ins `rd`, `rmdir`, `del`, and `erase` their own checks, separate from the `rm` critical-path list. For `Remove-Item`, the outcome depends on the target, and the first matching case applies:
