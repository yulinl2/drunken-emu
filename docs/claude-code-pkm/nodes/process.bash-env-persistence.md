---
id: process.bash-env-persistence
kind: process
status: VERIFIED
title: "Bash environment persistence"
sources: [S6]
---

# Bash environment persistence

**Sources:** [S6](src.s6.md)

Variables set with export do not persist across Bash commands. Aliases and functions from the shell startup file are available. CLAUDE_ENV_FILE makes variables persist ([CLAUDE_ENV_FILE](env.claude-env-file.md)).
