---
id: hook-field.shell
kind: hook-field
status: VERIFIED
title: "shell"
sources: [S85]
---

# shell

**Sources:** [S85](src.s85.md)

Shell to use for this hook. Accepts `"bash"` or `"powershell"`. Defaults to `"bash"`, or to `"powershell"` on Windows when Git Bash isn't installed. Setting `"powershell"` runs the command via PowerShell on Windows. Does not require `CLAUDE_CODE_USE_POWERSHELL_TOOL` since hooks spawn PowerShell directly. Ignored when `args` is set (required: no)
