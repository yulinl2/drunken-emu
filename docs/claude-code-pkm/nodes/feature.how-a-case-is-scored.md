---
id: feature.how-a-case-is-scored
kind: feature
status: VERIFIED
title: "How a case is scored"
sources: [S47]
---

# How a case is scored

**Sources:** [S47](src.s47.md)

One run of a non-deterministic agent tells you little, so each case runs three times by default. A run's score is the fraction of its graders that passed, weighted if you set weights, and the case's score is the mean across its runs. A case passes when its score meets the `--threshold`, `1.0` by default.
