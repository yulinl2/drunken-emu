---
id: process.foreground-to-background
kind: process
status: VERIFIED
title: "Foreground command moves to the background"
sources: [S6]
---

# Foreground command moves to the background

**Sources:** [S6](src.s6.md)

A foreground command that reaches its timeout is moved to the background, not stopped, unless it starts with sleep. CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1, or bare mode, stops it instead ([CLAUDE_CODE_DISABLE_BACKGROUND_TASKS](env.claude-code-disable-background-tasks.md)).
