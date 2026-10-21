---
id: env.bash-default-timeout-ms
kind: env
status: VERIFIED
title: "BASH_DEFAULT_TIMEOUT_MS"
sources: [S6]
---

# BASH_DEFAULT_TIMEOUT_MS

**Sources:** [S6](src.s6.md)

The default timeout when Claude passes none; 2 minutes out of the box. Above 1,800,000 ms it also replaces the 30-minute background default.

## Linked from

- [Background time limit](process.background-time-limit.md)
- [Bash](tool.bash.md)
