---
id: tool.exit-worktree
kind: tool
status: VERIFIED
title: "ExitWorktree"
sources: [S6, S7]
---

# ExitWorktree

**Sources:** [S6](src.s6.md), [S7](src.s7.md)

Permission: No. Leaves a worktree session. Refuses removal with uncommitted or unmerged work, unless discard_changes is set. Here: deferred.
