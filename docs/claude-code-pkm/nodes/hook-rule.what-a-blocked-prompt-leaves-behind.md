---
id: hook-rule.what-a-blocked-prompt-leaves-behind
kind: hook-rule
status: VERIFIED
title: "What a blocked prompt leaves behind"
sources: [S85]
---

# What a blocked prompt leaves behind

**Sources:** [S85](src.s85.md)

A blocked prompt never reaches Claude, but its text isn't removed everywhere. By default the block message shown to the user ends with `Original prompt:` followed by the submitted text, and Claude Code writes that message to the session's transcript file on disk. To leave the text out of the message, print JSON with `"suppressOriginalPrompt": true` inside `hookSpecificOutput`. This works whether t
