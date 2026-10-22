---
id: feature.runs-fail-with-a-usage-limit-or-rate-limit-error-partway-thr
kind: feature
status: VERIFIED
title: "Runs fail with a usage-limit or rate-limit error partway through"
sources: [S47]
---

# Runs fail with a usage-limit or rate-limit error partway through

**Sources:** [S47](src.s47.md)

Runs that end with a usage-limit or rate-limit error score 0 without grading, and the command exits non-zero. The suite still finishes and isn't marked `partial`. Re-run after the limit resets, with `--runs 1` or a `--case` filter if you need to stay under it.
