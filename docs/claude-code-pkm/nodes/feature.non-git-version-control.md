---
id: feature.non-git-version-control
kind: feature
status: VERIFIED
title: "Non-git version control"
sources: [S30]
---

# Non-git version control

**Sources:** [S30](src.s30.md)

Worktree isolation uses git by default. For SVN, Perforce, Mercurial, or other systems, configure `WorktreeCreate` and `WorktreeRemove` hooks to provide custom creation and cleanup logic. Because the hook replaces the default git behavior, `.worktreeinclude` is not processed when you use `--worktree`. Copy any local configuration files inside your hook script instead.
