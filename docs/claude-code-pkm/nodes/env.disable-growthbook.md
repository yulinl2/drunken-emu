---
id: env.disable-growthbook
kind: env
status: VERIFIED
title: "DISABLE_GROWTHBOOK"
sources: [S81]
---

# DISABLE_GROWTHBOOK

**Sources:** [S81](src.s81.md)

Set to `1` or `true` to disable GrowthBook feature-flag fetching and use code defaults for every flag. This makes Remote Control and the other features that need feature-flag fetching unavailable. Setting it to `0` or `false` leaves fetching on. Telemetry event logging stays on unless `DISABLE_TELEMETRY` is also set
