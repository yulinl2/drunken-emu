---
id: feature.manage-sessions-from-the-shell
kind: feature
status: VERIFIED
title: "Manage sessions from the shell"
sources: [S26]
---

# Manage sessions from the shell

**Sources:** [S26](src.s26.md)

Every background session has a short ID you can use from the shell. The ID is printed when you start a session with `claude --bg`, and each session's ID is its directory name under `~/.claude/jobs/`. These commands are useful for scripting or when you don't want to open agent view.
