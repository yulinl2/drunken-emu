---
id: process.background-time-limit
kind: process
status: VERIFIED
title: "Background time limit"
sources: [S6]
---

# Background time limit

**Sources:** [S6](src.s6.md)

Background Bash and PowerShell commands get 30 minutes by default, or the timeout passed with run_in_background, up to a 2-hour maximum. The limit applies only in unattended runs: -p, the SDK, CI and cloud sessions. A local terminal session has none. A command that moves to the background at its timeout gets 30 minutes from the move. Variables that raise the limits: [BASH_DEFAULT_TIMEOUT_MS](env.bash-default-timeout-ms.md) and [BASH_MAX_TIMEOUT_MS](env.bash-max-timeout-ms.md).

## Linked from

- [/tasks](cmd.tasks.md)
- [Background task](term.background-task.md)
- [Bash](tool.bash.md)
