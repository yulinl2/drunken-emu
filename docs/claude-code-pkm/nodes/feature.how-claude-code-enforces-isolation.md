---
id: feature.how-claude-code-enforces-isolation
kind: feature
status: VERIFIED
title: "How Claude Code enforces isolation"
sources: [S30]
---

# How Claude Code enforces isolation

**Sources:** [S30](src.s30.md)

While a session is isolated in a worktree, Claude Code blocks the tool calls the checks below define. The same rules apply whether you started the session with `--worktree`, Claude entered a worktree with `EnterWorktree`, or you resumed a worktree session.
