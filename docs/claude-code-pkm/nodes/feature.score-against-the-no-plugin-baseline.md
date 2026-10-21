---
id: feature.score-against-the-no-plugin-baseline
kind: feature
status: VERIFIED
title: "Score against the no-plugin baseline"
sources: [S47]
---

# Score against the no-plugin baseline

**Sources:** [S47](src.s47.md)

When a plugin is under test, a case normally runs in two arms. The with-arm is its runs with the plugin loaded, and the without-arm is the same number of runs with no plugin at all. The summary and report show both scores and `Δ`, the with-arm score minus the without-arm score.
