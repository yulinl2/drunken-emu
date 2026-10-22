---
id: tool.background-commands
kind: tool
status: VERIFIED
title: "Background commands"
sources: [S82]
---

# Background commands

**Sources:** [S82](src.s82.md)

For long-running processes such as dev servers or watch builds, Claude can set `run_in_background: true` to start the command as a background task and continue working while it runs. List and stop background tasks with `/tasks`. After you stop one there, or from a connected client such as the desktop app, Claude moves on instead of waiting for it. If a subagent started the command, it's that subag
