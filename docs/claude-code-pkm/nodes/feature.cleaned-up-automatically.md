---
id: feature.cleaned-up-automatically
kind: feature
status: VERIFIED
title: "Cleaned up automatically"
sources: [S16]
---

# Cleaned up automatically

**Sources:** [S16](src.s16.md)

Claude Code deletes the files in the paths below once they're older than `cleanupPeriodDays`, as long as it can safely determine the retention period. The default is 30 days and the minimum is 1; setting `0` fails with a validation error. The same age cutoff applies to automatic removal of orphaned worktrees.
