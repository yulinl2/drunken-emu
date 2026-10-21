---
id: feature.review-denials
kind: feature
status: VERIFIED
title: "Review denials"
sources: [S64]
---

# Review denials

**Sources:** [S64](src.s64.md)

To review and retry actions the auto mode classifier denied, open `/permissions` and select the Recently denied tab, where Claude Code records each denial. Press `r` on a denied action to mark it for retry: when you exit the dialog, Claude Code sends a message telling the model it may retry that tool call and resumes the conversation.
