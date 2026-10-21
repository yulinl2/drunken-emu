---
id: feature.replace-worktree-creation-with-a-hook
kind: feature
status: VERIFIED
title: "Replace worktree creation with a hook"
sources: [S30]
---

# Replace worktree creation with a hook

**Sources:** [S30](src.s30.md)

Configure a `WorktreeCreate` hook to replace the default `git worktree` logic entirely, including placing worktrees somewhere other than `.claude/worktrees/`. For a complete example, see Non-git version control.
