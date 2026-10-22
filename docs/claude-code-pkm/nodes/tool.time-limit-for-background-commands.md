---
id: tool.time-limit-for-background-commands
kind: tool
status: VERIFIED
title: "Time limit for background commands"
sources: [S82]
---

# Time limit for background commands

**Sources:** [S82](src.s82.md)

In a session that runs unattended, such as a run with the `-p` flag, an Agent SDK application, a CI job, or a cloud session, background Bash and PowerShell commands have a time limit. A local session you work in from a terminal, the desktop app, or the VS Code extension has no time limit on background commands.
