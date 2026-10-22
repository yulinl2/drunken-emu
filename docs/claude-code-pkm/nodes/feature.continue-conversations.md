---
id: feature.continue-conversations
kind: feature
status: VERIFIED
title: "Continue conversations"
sources: [S38]
---

# Continue conversations

**Sources:** [S38](src.s38.md)

Use `--continue` to continue the most recent conversation, or `--resume` with a session ID to continue a specific conversation. On Claude Code v2.1.257 or later, when you pass `--continue`, Claude Code opens a background session that has finished, but not one that is still running. This example runs a review, then sends follow-up prompts:
