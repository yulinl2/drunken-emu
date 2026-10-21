---
id: hook.worktree-create
kind: hook
status: VERIFIED
title: "WorktreeCreate"
sources: [S2]
---

# WorktreeCreate

**Sources:** [S2](src.s2.md)

Fires when a worktree is created by --worktree, isolation: worktree, or a background session. Replaces the default git behavior. Output: a path on stdout, or hookSpecificOutput.worktreePath over HTTP. Any non-zero exit fails creation. See [Worktrees](feature.worktrees.md).

## Linked from

- [Worktrees](feature.worktrees.md)
