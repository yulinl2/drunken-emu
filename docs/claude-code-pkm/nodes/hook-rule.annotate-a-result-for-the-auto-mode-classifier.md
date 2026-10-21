---
id: hook-rule.annotate-a-result-for-the-auto-mode-classifier
kind: hook-rule
status: VERIFIED
title: "Annotate a result for the auto mode classifier"
sources: [S85]
---

# Annotate a result for the auto mode classifier

**Sources:** [S85](src.s85.md)

Return `classifierContext` to send a short note about the tool call's result to the auto mode classifier rather than to Claude. The classifier never receives tool results themselves, so this field is the supported way to tell it something about what a call returned before it reviews later actions. The field requires Claude Code v2.1.236 or later.
