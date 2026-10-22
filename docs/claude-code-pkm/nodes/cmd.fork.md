---
id: cmd.fork
kind: command
status: VERIFIED
title: "/fork"
sources: [S80]
---

# /fork

**Sources:** [S80](src.s80.md)

Copy the current conversation into a new background session and keep working here. Pass a prompt and the copy starts working on it immediately; without one it waits in agent view for its first prompt. Except when the copy edits in place, Claude Code instructs it to create a worktree of its own before making code changes; the isolation instruction requires Claude Code v2.1.221 or later. To hand a side task to a subagent whose result comes back into this conversation, use `/subtask`; to switch into a copy yourself, use `/branch`. When agent view is turned off, `/fork` starts a forked subagent instead
