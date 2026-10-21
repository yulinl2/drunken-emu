---
id: env.claude-code-resume-prompt
kind: env
status: VERIFIED
title: "CLAUDE_CODE_RESUME_PROMPT"
sources: [S81]
---

# CLAUDE_CODE_RESUME_PROMPT

**Sources:** [S81](src.s81.md)

Override the continuation message Claude Code sends to Claude when `CLAUDE_CODE_RESUME_INTERRUPTED_TURN` continues an interrupted turn instead of resending its prompt, or when you resume a deferred tool call with `-p`. Defaults to `Continue from where you left off.`. An empty string uses the default
