---
id: env.claude-code-disable-mounted-drive-rm-prompt
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_MOUNTED_DRIVE_RM_PROMPT"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_MOUNTED_DRIVE_RM_PROMPT

**Sources:** [S81](src.s81.md)

Set to `1` to turn off the mounted drive prompt for paths such as `/Volumes/USB`. Set it in the environment that launches Claude Code, because Claude Code ignores it in a settings `env` block. Requires Claude Code v2.1.304 or later
