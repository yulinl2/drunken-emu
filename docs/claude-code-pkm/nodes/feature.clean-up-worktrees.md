---
id: feature.clean-up-worktrees
kind: feature
status: VERIFIED
title: "Clean up worktrees"
sources: [S30]
---

# Clean up worktrees

**Sources:** [S30](src.s30.md)

When you exit an interactive worktree session, Claude checks the worktree for work that removal would delete: changed or untracked files, uncommitted work inside checked-out submodules, and new commits. These rules apply to worktrees Claude created with git. For a worktree your WorktreeCreate hook created, see WorktreeRemove instead.
