---
id: env.claude-code-shell-prefix
kind: env
status: VERIFIED
title: "CLAUDE_CODE_SHELL_PREFIX"
sources: [S81]
---

# CLAUDE_CODE_SHELL_PREFIX

**Sources:** [S81](src.s81.md)

Command prefix that wraps shell commands Claude Code spawns: Bash tool calls, hook commands, status line commands, and stdio MCP server startup commands. PowerShell hooks and exec-form hooks run without the prefix. Useful for logging or auditing. Setting a bare executable path such as `/path/to/logger.sh` runs each command as `/path/to/logger.sh ''`. The wrapper receives the command line as a single shell-quoted argument in `$1`, so the wrapper must re-evaluate `$1` with a shell, for example `exec bash -c "$1"`. Treating `$1` as a bare executable path breaks stdio MCP servers that pass arguments such as `npx -y `. For Bash tool calls, `$1` contains the full shell invocation Claude Code assembles, including environment setup, not only the command Claude ran
