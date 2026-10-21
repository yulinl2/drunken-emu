---
id: mod.add-a-command-or-a-tool
kind: mod
status: VERIFIED
title: "Add a command or a tool"
sources: [S56]
---

# Add a command or a tool

**Sources:** [S56](src.s56.md)

A mod can add a command for the user to run and a tool for Claude to call. Register both in a `session.start` hook. Claude Code waits for that hook before the first prompt, so what you register is available from the first turn.
