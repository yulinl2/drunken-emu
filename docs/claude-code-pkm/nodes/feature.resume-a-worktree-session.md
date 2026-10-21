---
id: feature.resume-a-worktree-session
kind: feature
status: VERIFIED
title: "Resume a worktree session"
sources: [S30]
---

# Resume a worktree session

**Sources:** [S30](src.s30.md)

When you resume a session that ended inside a worktree without exiting it, Claude Code returns the session to that worktree. This holds for interactive resumes, for `--continue` and `--resume` in non-interactive mode with `-p`, and for the Agent SDK. `--continue` picks the most recent session recorded under the directory you launch from. Back inside the worktree, Claude can still exit it with the
