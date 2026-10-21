---
id: tool.foreground-commands-that-move-to-the-background
kind: tool
status: VERIFIED
title: "Foreground commands that move to the background"
sources: [S82]
---

# Foreground commands that move to the background

**Sources:** [S82](src.s82.md)

When a foreground command reaches its timeout without finishing, Claude Code moves it to the background instead of stopping it, unless the command starts with `sleep`. A moved command's time limit counts from the move, and a foreground subagent's moved command still stops when that subagent's run ends.
