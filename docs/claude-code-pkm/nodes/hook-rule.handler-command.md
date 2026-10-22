---
id: hook-rule.handler-command
kind: hook-rule
status: VERIFIED
title: "Handler type: command"
sources: [S2]
---

# Handler type: command

**Sources:** [S2](src.s2.md)

Runs a shell command or an executable. Fields: command, args (exec form, no shell), shell (bash or powershell), async, asyncRewake, timeout, statusMessage, onFailure and if. On Windows, command must be a real .exe when args is set.

## Linked from

- [Hook](term.hook.md)
