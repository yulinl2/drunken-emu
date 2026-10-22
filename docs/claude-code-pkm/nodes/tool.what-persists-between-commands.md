---
id: tool.what-persists-between-commands
kind: tool
status: VERIFIED
title: "What persists between commands"
sources: [S82]
---

# What persists between commands

**Sources:** [S82](src.s82.md)

When Claude runs `cd` in the main session, the new working directory carries over to later Bash commands as long as it stays inside the project directory or an additional working directory you added with `--add-dir`, `/add-dir`, or `additionalDirectories` in settings. This includes commands Claude runs in response to your later messages.
