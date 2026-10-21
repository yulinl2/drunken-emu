---
id: feature.how-evaluation-works
kind: feature
status: VERIFIED
title: "How evaluation works"
sources: [S37]
---

# How evaluation works

**Sources:** [S37](src.s37.md)

`/goal` is a wrapper around a session-scoped prompt-based Stop hook. Each time Claude finishes a turn, Claude Code sends the condition and the conversation so far to your configured small fast model. The model returns one of three verdicts, each with a short reason:
