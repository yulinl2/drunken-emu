---
id: feature.ask-claude-to-create-a-worktree
kind: feature
status: VERIFIED
title: "Ask Claude to create a worktree"
sources: [S30]
---

# Ask Claude to create a worktree

**Sources:** [S30](src.s30.md)

You can also ask Claude to "work in a worktree" during a session, and it creates one with the `EnterWorktree` tool. Once in a worktree, Claude can switch directly to another one under `.claude/worktrees/` by calling `EnterWorktree` with the target path; the previous worktree stays on disk untouched.
