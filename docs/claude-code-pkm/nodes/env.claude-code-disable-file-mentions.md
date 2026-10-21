---
id: env.claude-code-disable-file-mentions
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_FILE_MENTIONS"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_FILE_MENTIONS

**Sources:** [S81](src.s81.md)

Set to `1` to stop Claude Code from expanding `@` mentions of files and directories. Claude instead gets the mentioned paths with a note to read them using its file tools. Ignored in project and local settings. Requires Claude Code v2.1.299 or later
