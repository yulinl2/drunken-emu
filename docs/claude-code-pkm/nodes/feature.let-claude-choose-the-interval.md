---
id: feature.let-claude-choose-the-interval
kind: feature
status: VERIFIED
title: "Let Claude choose the interval"
sources: [S36]
---

# Let Claude choose the interval

**Sources:** [S36](src.s36.md)

When you omit the interval, Claude chooses one dynamically instead of running on a fixed cron schedule. After each iteration it picks a delay between one minute and one hour based on what it observed: short waits while a build is finishing or a PR is active, longer waits when nothing is pending. The chosen delay and the reason for it are printed at the end of each iteration.
