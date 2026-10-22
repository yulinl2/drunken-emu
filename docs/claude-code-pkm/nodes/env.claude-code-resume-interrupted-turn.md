---
id: env.claude-code-resume-interrupted-turn
kind: env
status: VERIFIED
title: "CLAUDE_CODE_RESUME_INTERRUPTED_TURN"
sources: [S81]
---

# CLAUDE_CODE_RESUME_INTERRUPTED_TURN

**Sources:** [S81](src.s81.md)

Set to `1` to automatically resume if the previous session ended mid-turn. Used in SDK mode so the model continues without requiring the SDK to re-send the prompt. To turn this off, unset the variable or set it to `0`. For the VS Code chat panel, see Continue conversations after a reload
