---
id: feature.sessions-in-other-worktrees-and-projects
kind: feature
status: VERIFIED
title: "Sessions in other worktrees and projects"
sources: [S20]
---

# Sessions in other worktrees and projects

**Sources:** [S20](src.s20.md)

When you select a session from another worktree of the same repository, Claude Code resumes it in place; when the session's own worktree no longer exists, Claude Code resumes it in your current directory. When you select a session from an unrelated project, Claude Code copies a `cd` and resume command to your clipboard instead. If that project's directory no longer exists, Claude Code resumes the
