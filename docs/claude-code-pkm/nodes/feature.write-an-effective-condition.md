---
id: feature.write-an-effective-condition
kind: feature
status: VERIFIED
title: "Write an effective condition"
sources: [S37]
---

# Write an effective condition

**Sources:** [S37](src.s37.md)

The evaluator judges your condition against what Claude has surfaced in the conversation. It doesn't run commands or read files independently, so write the condition as something Claude's own output can demonstrate. "All tests in `test/auth` pass" works because Claude runs the tests and the result appears in the transcript for the evaluator to read.
