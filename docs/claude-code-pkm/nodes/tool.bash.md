---
id: tool.bash
kind: tool
status: VERIFIED
title: "Bash"
sources: [S6, S8]
---

# Bash

**Sources:** [S6](src.s6.md), [S8](src.s8.md)

Permission: Yes. Runs shell commands, each in a separate process. Limits: [Bash output limits](process.bash-output-limits.md) and [Background time limit](process.background-time-limit.md). Environment: [BASH_DEFAULT_TIMEOUT_MS](env.bash-default-timeout-ms.md) and [BASH_MAX_TIMEOUT_MS](env.bash-max-timeout-ms.md). Here: direct.

## Linked from

- [Built-in tool](term.built-in-tool.md)
- [CLAUDE_ENV_FILE](env.claude-env-file.md)
- [Permission column](term.permission-column.md)
- [Sandboxed Bash tool](feature.sandboxing.md)
- [Specifier: Bash command patterns](permission-rule.specifier-bash.md)
