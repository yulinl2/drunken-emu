---
id: feature.check-the-retention-sweep
kind: feature
status: VERIFIED
title: "Check the retention sweep"
sources: [S65]
---

# Check the retention sweep

**Sources:** [S65](src.s65.md)

To give every machine the same retention period, set `cleanupPeriodDays` in managed settings. To check that machines run the sweep with that value, collect the `retention_sweep` event. `period_days` and the counters are strings, so cast them to numbers before you compare them.
