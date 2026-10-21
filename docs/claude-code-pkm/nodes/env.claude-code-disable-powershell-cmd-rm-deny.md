---
id: env.claude-code-disable-powershell-cmd-rm-deny
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_POWERSHELL_CMD_RM_DENY"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_POWERSHELL_CMD_RM_DENY

**Sources:** [S81](src.s81.md)

Set to `1` to turn off the PowerShell tool check that denies the `cmd` built-ins `rd`, `rmdir`, `del`, and `erase` on a system path, such as a drive root or your home directory. Claude Code ignores this variable in a settings file's `env` block. Requires Claude Code v2.1.283 or later
