---
id: env.claude-code-send-feedback
kind: env
status: VERIFIED
title: "CLAUDE_CODE_SEND_FEEDBACK"
sources: [S81]
---

# CLAUDE_CODE_SEND_FEEDBACK

**Sources:** [S81](src.s81.md)

Set to `0` to turn off Claude-drafted feedback for a session. Set to `1` to turn it on where your account already has access; the variable can't grant access itself, and the other switches that turn feedback off, such as `DISABLE_FEEDBACK_COMMAND` and the `feedbackDrafts` setting's `off` value, still apply
