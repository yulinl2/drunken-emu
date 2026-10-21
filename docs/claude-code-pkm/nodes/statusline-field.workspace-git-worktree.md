---
id: statusline-field.workspace-git-worktree
kind: statusline-field
status: VERIFIED
title: "workspace.git_worktree"
sources: [S78]
---

# workspace.git_worktree

**Sources:** [S78](src.s78.md)

Git worktree name when the current directory is inside a linked worktree created with `git worktree add`. Absent in the main working tree. Populated for any git worktree, unlike `worktree.*`, which is present only while the session is in a worktree session
