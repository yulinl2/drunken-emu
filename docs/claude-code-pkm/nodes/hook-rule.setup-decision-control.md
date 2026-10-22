---
id: hook-rule.setup-decision-control
kind: hook-rule
status: VERIFIED
title: "Setup decision control"
sources: [S85]
---

# Setup decision control

**Sources:** [S85](src.s85.md)

Setup hooks can't block; execution continues on any exit code. On every exit code, Claude Code discards a Setup hook's JSON output fields, such as `systemMessage`, `continue`, and `hookSpecificOutput.additionalContext`. With `-p`, a Setup hook's stdout, stderr, and exit code appear in the run's output only as `hook_response` events when you launch with `--output-format stream-json --verbose`.
