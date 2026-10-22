---
id: feature.claude-worktrees-is-filling-up
kind: feature
status: VERIFIED
title: ".claude/worktrees/ is filling up"
sources: [S26]
---

# .claude/worktrees/ is filling up

**Sources:** [S26](src.s26.md)

Deleting a session in agent view removes the worktree Claude created for it, but some deletes keep the worktree or leave its directory on disk, so leftover directories can accumulate. Directories git no longer recognizes don't appear in `git worktree list`, so remove those by hand.
