---
id: feature.how-file-edits-are-isolated
kind: feature
status: VERIFIED
title: "How file edits are isolated"
sources: [S26]
---

# How file edits are isolated

**Sources:** [S26](src.s26.md)

When you dispatch a background session from agent view or start one with `claude --bg`, the session starts in your working directory. Before editing files, Claude moves the session into an isolated git worktree under `.claude/worktrees/`, so parallel sessions can read the same checkout but each writes to its own. Once the session is in its worktree, Claude Code enforces worktree isolation for the
