---
id: hook-rule.filechanged
kind: hook-rule
status: VERIFIED
title: "FileChanged"
sources: [S85]
---

# FileChanged

**Sources:** [S85](src.s85.md)

Runs when a watched file changes on disk. Claude Code detects changes with a filesystem watcher, not by inspecting tool calls, so it runs the hook no matter what changed the file: an `Edit` or `Write` tool call, a script Claude runs with `Bash`, or a process outside Claude Code entirely. A common use is reloading environment variables when project configuration files change.
