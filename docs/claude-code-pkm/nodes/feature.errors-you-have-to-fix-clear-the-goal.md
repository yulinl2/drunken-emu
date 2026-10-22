---
id: feature.errors-you-have-to-fix-clear-the-goal
kind: feature
status: VERIFIED
title: "Errors you have to fix clear the goal"
sources: [S37]
---

# Errors you have to fix clear the goal

**Sources:** [S37](src.s37.md)

If a turn fails on an error that won't clear until you fix it, Claude Code clears the goal and prints a warning naming the cause. The warning starts with `Goal cleared after an unrecoverable error` and ends with `Run /goal again to continue`. Fix the cause, then set the goal again with `/goal `. Four kinds of failure clear the goal:
