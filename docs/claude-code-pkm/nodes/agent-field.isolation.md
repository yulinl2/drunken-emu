---
id: agent-field.isolation
kind: agent-field
status: VERIFIED
title: "isolation"
sources: [S25]
---

# isolation

**Sources:** [S25](src.s25.md)

Set to `worktree` to run the subagent in a temporary git worktree, giving it an isolated copy of the repository branched by default from your default branch rather than the parent session's `HEAD`. The worktree is automatically cleaned up if the subagent makes no changes (required: No)
