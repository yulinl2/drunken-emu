---
id: feature.start-claude-in-a-worktree
kind: feature
status: VERIFIED
title: "Start Claude in a worktree"
sources: [S30]
---

# Start Claude in a worktree

**Sources:** [S30](src.s30.md)

Pass `--worktree` or `-w` with a name to create an isolated worktree and start Claude in it. By default, the worktree is created under `.claude/worktrees//` at your repository root, on a new branch named `worktree-`:
