---
id: env.claude-code-use-powershell-tool
kind: env
status: VERIFIED
title: "CLAUDE_CODE_USE_POWERSHELL_TOOL"
sources: [S6]
---

# CLAUDE_CODE_USE_POWERSHELL_TOOL

**Sources:** [S6](src.s6.md)

1 enables the PowerShell tool on Bedrock, Agent Platform and Foundry, and 0 turns it off on Windows. Required on Linux, macOS and WSL, which also need pwsh 7 or later ([PowerShell](tool.powershell.md)).

## Linked from

- [Bash deny also turns off PowerShell on Windows](permission-rule.bash-deny-disables-powershell.md)
