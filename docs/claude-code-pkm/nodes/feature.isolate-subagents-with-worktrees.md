---
id: feature.isolate-subagents-with-worktrees
kind: feature
status: VERIFIED
title: "Isolate subagents with worktrees"
sources: [S30]
---

# Isolate subagents with worktrees

**Sources:** [S30](src.s30.md)

Subagents can run in their own worktrees so parallel edits don't conflict. Ask Claude to "use worktrees for your agents", or make the isolation permanent for a custom subagent by adding `isolation: worktree` to its frontmatter.
