---
id: feature.set-up-the-worktree-environment
kind: feature
status: VERIFIED
title: "Set up the worktree environment"
sources: [S30]
---

# Set up the worktree environment

**Sources:** [S30](src.s30.md)

A worktree is a fresh checkout, so initialize your development environment there: ask Claude to install dependencies, or run your project's setup yourself in the worktree directory under `.claude/worktrees/`. To carry gitignored files such as `.env` into every new worktree automatically, add a `.worktreeinclude` file.
