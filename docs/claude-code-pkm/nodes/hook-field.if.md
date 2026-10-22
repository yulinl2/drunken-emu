---
id: hook-field.if
kind: hook-field
status: VERIFIED
title: "if"
sources: [S85]
---

# if

**Sources:** [S85](src.s85.md)

Permission rule syntax to filter when this hook runs, such as `"Bash(git *)"` or `"Edit(*.ts)"`. The hook command only runs if the tool call matches the pattern. See the Bash matching table for how Bash patterns evaluate against subcommands, `$()`, and backticks. Only evaluated on tool events: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, and `PermissionDenied`. On other events, a hook with `if` set never runs (required: no)
