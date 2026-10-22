---
id: feature.claude-code-can-t-enter-the-worktree-at-startup
kind: feature
status: VERIFIED
title: "Claude Code can't enter the worktree at startup"
sources: [S30]
---

# Claude Code can't enter the worktree at startup

**Sources:** [S30](src.s30.md)

When Claude Code can't enter the worktree directory at startup, it prints an error naming the path and exits with code 1. This can happen when a `WorktreeCreate` hook prints something other than the directory it created, or when the directory was deleted after it was set up.
