---
id: permission-rule.powershell
kind: permission-rule
status: VERIFIED
title: "PowerShell"
sources: [S66]
---

# PowerShell

**Sources:** [S66](src.s66.md)

PowerShell permission rules use the same shape as Bash rules. Wildcards with `*` match at any position, the `:*` suffix is equivalent to a trailing ` *`, and a bare `PowerShell` or `PowerShell(*)` matches every command. This configuration allows `Get-ChildItem` and `git commit` commands while blocking `Remove-Item`:
