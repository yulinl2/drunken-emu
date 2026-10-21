---
id: permission-rule.bash-deny-disables-powershell
kind: permission-rule
status: VERIFIED
title: "Bash deny also turns off PowerShell on Windows"
sources: [S6]
---

# Bash deny also turns off PowerShell on Windows

**Sources:** [S6](src.s6.md)

On Windows with Git Bash installed, a Bash deny (scoped or bare, from settings or --disallowedTools) also turns the PowerShell tool off for the session. Keep it on with CLAUDE_CODE_USE_POWERSHELL_TOOL=1 or a scoped PowerShell rule. See [CLAUDE_CODE_USE_POWERSHELL_TOOL](env.claude-code-use-powershell-tool.md).
