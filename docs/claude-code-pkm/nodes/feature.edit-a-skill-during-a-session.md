---
id: feature.edit-a-skill-during-a-session
kind: feature
status: VERIFIED
title: "Edit a skill during a session"
sources: [S32]
---

# Edit a skill during a session

**Sources:** [S32](src.s32.md)

Claude Code watches skill directories for file changes, except in bare mode. When you add, edit, or remove a skill under `~/.claude/skills/`, the project `.claude/skills/`, or a `.claude/skills/` inside an `--add-dir` directory, Claude Code picks up the change within the current session, without a restart.
