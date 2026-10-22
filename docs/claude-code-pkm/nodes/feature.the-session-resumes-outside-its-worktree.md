---
id: feature.the-session-resumes-outside-its-worktree
kind: feature
status: VERIFIED
title: "The session resumes outside its worktree"
sources: [S30]
---

# The session resumes outside its worktree

**Sources:** [S30](src.s30.md)

When you resume a session interactively and Claude Code can't return it to its worktree, Claude Code says so with one of the messages below. When Claude Code clears the worktree binding, it records the clear in the session transcript. If you suppress transcript writes, the message says instead that the binding could not be cleared and that Claude Code will re-check the worktree on a later resume.
