---
id: env.claude-code-bs-as-ctrl-backspace
kind: env
status: VERIFIED
title: "CLAUDE_CODE_BS_AS_CTRL_BACKSPACE"
sources: [S81]
---

# CLAUDE_CODE_BS_AS_CTRL_BACKSPACE

**Sources:** [S81](src.s81.md)

Set to `0` to make Claude Code read the `0x08` byte, also written `^H`, as plain Backspace, or `1` to read it as Ctrl+Backspace. Either value replaces the platform default. By default, Claude Code reads it as Ctrl+Backspace on Windows, except when `TERM_PROGRAM` is `mintty` or `TERM` is `cygwin`, and as plain Backspace on macOS and Linux. Set `0` in a Windows terminal where Backspace deletes a whole word
