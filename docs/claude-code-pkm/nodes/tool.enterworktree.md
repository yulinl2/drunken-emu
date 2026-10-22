---
id: tool.enterworktree
kind: tool
status: VERIFIED
title: "EnterWorktree"
sources: [S82]
---

# EnterWorktree

**Sources:** [S82](src.s82.md)

Creates an isolated git worktree and switches into it. Pass a `path` to switch into an existing worktree instead of creating a new one. On first entry the target may be a worktree of the current repository or, in a multi-repo workspace, of a repository nested inside it. Before v2.1.203, a nested repository's worktree was rejected. A `path` outside `.claude/worktrees/` prompts for your approval before entering, since it moves the session's working directory and write access to that location. New-worktree creation and paths under `.claude/worktrees/` don't prompt. Before v2.1.206, Claude entered paths outside `.claude/worktrees/` without a prompt. From within a worktree session, or from a subagent with a pinned working directory such as `isolation: worktree`, only the `path` form is available and the target must be under `.claude/worktrees/` of the session's repository (permission required: Yes)
