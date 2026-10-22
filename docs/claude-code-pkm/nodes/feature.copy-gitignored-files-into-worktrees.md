---
id: feature.copy-gitignored-files-into-worktrees
kind: feature
status: VERIFIED
title: "Copy gitignored files into worktrees"
sources: [S30]
---

# Copy gitignored files into worktrees

**Sources:** [S30](src.s30.md)

A worktree is a fresh checkout, so untracked files like `.env` or `.env.local` from your main repository are not present. To copy them automatically when Claude creates a worktree, add a `.worktreeinclude` file to your project root.
