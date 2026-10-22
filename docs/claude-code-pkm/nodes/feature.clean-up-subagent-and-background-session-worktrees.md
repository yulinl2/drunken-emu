---
id: feature.clean-up-subagent-and-background-session-worktrees
kind: feature
status: VERIFIED
title: "Clean up subagent and background-session worktrees"
sources: [S30]
---

# Clean up subagent and background-session worktrees

**Sources:** [S30](src.s30.md)

Claude Code runs a periodic sweep that removes worktrees that Claude created for subagents and background sessions once they are older than your `cleanupPeriodDays` setting, following the retention sweep rules.
