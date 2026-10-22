---
id: process.bash-cd-persistence
kind: process
status: VERIFIED
title: "Bash cd persistence"
sources: [S6]
---

# Bash cd persistence

**Sources:** [S6](src.s6.md)

A cd in the main session carries to later Bash commands while it stays inside the project or an added directory. Subagent sessions never carry it. Outside those directories the working directory resets, and the result says so. [CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR](env.claude-bash-maintain-project-working-dir.md) turns the carry-over off.
