---
id: tool.exit-code-1-from-searches-and-git-diff-in-powershell
kind: tool
status: VERIFIED
title: "Exit code 1 from searches and git diff in PowerShell"
sources: [S82]
---

# Exit code 1 from searches and git diff in PowerShell

**Sources:** [S82](src.s82.md)

If a `grep` or `rg` search that matches nothing shows `Error: Exit code 1` when Claude runs it in the PowerShell tool, the search didn't fail. You don't need to do anything. The error can appear when the search is part of a longer command. For example, when `rg` exits with code 1, `rg foo / Out-Null` shows the error and `rg foo` doesn't.
