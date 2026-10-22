---
id: hook-rule.worktreecreate-output
kind: hook-rule
status: VERIFIED
title: "WorktreeCreate output"
sources: [S85]
---

# WorktreeCreate output

**Sources:** [S85](src.s85.md)

WorktreeCreate hooks don't use the standard allow/block decision model. Instead, the hook's success or failure determines the outcome. The hook must return the path to the created worktree directory:
