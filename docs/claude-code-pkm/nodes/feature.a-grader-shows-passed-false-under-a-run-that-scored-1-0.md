---
id: feature.a-grader-shows-passed-false-under-a-run-that-scored-1-0
kind: feature
status: VERIFIED
title: "A grader shows passed: false under a run that scored 1.0"
sources: [S47]
---

# A grader shows passed: false under a run that scored 1.0

**Sources:** [S47](src.s47.md)

That grader is excluded from the score by design in a two-arm run, and its `scored` field is `false`. See Score against the no-plugin baseline.
