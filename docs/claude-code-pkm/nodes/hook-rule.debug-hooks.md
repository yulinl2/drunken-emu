---
id: hook-rule.debug-hooks
kind: hook-rule
status: VERIFIED
title: "Debug hooks"
sources: [S85]
---

# Debug hooks

**Sources:** [S85](src.s85.md)

Hook execution details are written to the debug log file. Start Claude Code with `claude --debug-file ` to write the log to a known location, or run `claude --debug` and read the log at `~/.claude/debug/.txt`. The `--debug` flag doesn't print to the terminal.
