---
id: feature.worktree-creation-fails-on-a-symlinked-path
kind: feature
status: VERIFIED
title: "Worktree creation fails on a symlinked path"
sources: [S30]
---

# Worktree creation fails on a symlinked path

**Sources:** [S30](src.s30.md)

Claude Code refuses to create a worktree when `.claude`, `.claude/worktrees`, or the worktree directory itself is a symlink, and the error names the symlinked path. Remove the symlink and retry. Before v2.1.212, if the repository already contained a committed symlink at one of those paths, worktree creation followed it and could create files outside the repository.
