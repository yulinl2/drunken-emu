---
id: feature.claude-code-refuses-to-use-a-worktree
kind: feature
status: VERIFIED
title: "Claude Code refuses to use a worktree"
sources: [S30]
---

# Claude Code refuses to use a worktree

**Sources:** [S30](src.s30.md)

An error starting `Refusing to use as an isolation worktree` means Claude Code checked the directory's git identity before adopting it as a session's or subagent's isolated checkout, and declined it. The check runs whether Claude Code is creating the worktree, entering an existing one, or reusing one from an earlier run.
