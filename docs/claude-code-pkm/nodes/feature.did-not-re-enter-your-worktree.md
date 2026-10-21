---
id: feature.did-not-re-enter-your-worktree
kind: feature
status: VERIFIED
title: "Did not re-enter your worktree"
sources: [S30]
---

# Did not re-enter your worktree

**Sources:** [S30](src.s30.md)

Claude Code refused the worktree binding as unsafe; it clears the binding and the session continues without isolation. The message includes the specific refusal: match it under Claude Code refuses to use a worktree, since the fix is recreation for some refusals and a path change for others.
