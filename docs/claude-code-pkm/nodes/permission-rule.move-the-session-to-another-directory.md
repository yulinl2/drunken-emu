---
id: permission-rule.move-the-session-to-another-directory
kind: permission-rule
status: VERIFIED
title: "Move the session to another directory"
sources: [S66]
---

# Move the session to another directory

**Sources:** [S66](src.s66.md)

To move the session to a different primary working directory, rather than adding a directory alongside the current one, run `/cd `. Claude Code keeps the conversation, loads the new directory's `CLAUDE.md`, and prompts you to trust the workspace if you haven't worked in it before. Afterward, Claude Code finds the moved session when you run `--resume` from the new directory.
