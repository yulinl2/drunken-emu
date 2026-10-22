---
id: env.claude-code-disable-inline-shell-rm-prompt
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_INLINE_SHELL_RM_PROMPT"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_INLINE_SHELL_RM_PROMPT

**Sources:** [S81](src.s81.md)

Set to `1` to stop Claude Code from reading scripts passed to a shell with `-c`, such as `bash -c 'rm -rf ~'`, for critical-path removals. Claude Code still checks the shell variable and positional parameter targets in those scripts, and the other critical-path checks keep running. Set it in the environment that launches Claude Code, since Claude Code ignores a copy delivered through a settings `env` block. Requires Claude Code v2.1.288 or later
