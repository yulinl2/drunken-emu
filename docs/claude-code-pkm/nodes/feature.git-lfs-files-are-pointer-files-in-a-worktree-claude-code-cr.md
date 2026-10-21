---
id: feature.git-lfs-files-are-pointer-files-in-a-worktree-claude-code-cr
kind: feature
status: VERIFIED
title: "Git LFS files are pointer files in a worktree Claude Code created"
sources: [S30]
---

# Git LFS files are pointer files in a worktree Claude Code created

**Sources:** [S30](src.s30.md)

If you set up Git LFS with `git lfs install --local`, a worktree that Claude Code creates contains LFS pointer files instead of the real files. The `--local` flag writes the LFS filter into the repository's own `.git/config` rather than your global git config. A plain `git lfs install` writes to your global config and isn't affected. The same applies to any other filter driver defined in the repos
