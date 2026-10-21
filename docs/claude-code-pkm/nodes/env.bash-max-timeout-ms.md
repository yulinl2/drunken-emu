---
id: env.bash-max-timeout-ms
kind: env
status: VERIFIED
title: "BASH_MAX_TIMEOUT_MS"
sources: [S6]
---

# BASH_MAX_TIMEOUT_MS

**Sources:** [S6](src.s6.md)

The ceiling on requested timeouts; 10 minutes out of the box. Above 7,200,000 ms it also raises the 2-hour background cap.

## Linked from

- [Background time limit](process.background-time-limit.md)
- [Bash](tool.bash.md)
