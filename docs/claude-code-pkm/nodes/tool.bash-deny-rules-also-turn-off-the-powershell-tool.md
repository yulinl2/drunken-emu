---
id: tool.bash-deny-rules-also-turn-off-the-powershell-tool
kind: tool
status: VERIFIED
title: "Bash deny rules also turn off the PowerShell tool"
sources: [S82]
---

# Bash deny rules also turn off the PowerShell tool

**Sources:** [S82](src.s82.md)

On Windows with Git Bash installed, denying Bash also turns the PowerShell tool off for the session. This applies to scoped rules such as `Bash(git push *)` as well as a bare `Bash`, and to rules from one of your settings files or `--disallowedTools`. Claude Code does this because a `Bash` rule doesn't restrict the PowerShell tool, which has its own permission rules. With PowerShell left on, Claud
