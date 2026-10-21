---
id: env.claude-job-dir
kind: env
status: VERIFIED
title: "CLAUDE_JOB_DIR"
sources: [S81]
---

# CLAUDE_JOB_DIR

**Sources:** [S81](src.s81.md)

Set by Claude Code in each background session to that session's `~/.claude/jobs/` directory. Shell commands that the session runs inherit it. Write scratch files to `$CLAUDE_JOB_DIR/tmp`. Claude's `Write` and `Edit` calls there don't prompt for permission, and the directory is removed when the session is deleted
