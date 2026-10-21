---
id: env.claude-env-file
kind: env
status: VERIFIED
title: "CLAUDE_ENV_FILE"
sources: [S2, S6]
---

# CLAUDE_ENV_FILE

**Sources:** [S2](src.s2.md), [S6](src.s6.md)

A file path. In SessionStart hooks, export lines appended to it apply to later Bash commands. Set it before launch to make variables persist across Bash commands ([Bash](tool.bash.md)).

## Linked from

- [Bash environment persistence](process.bash-env-persistence.md)
