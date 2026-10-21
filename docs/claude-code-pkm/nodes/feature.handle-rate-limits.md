---
id: feature.handle-rate-limits
kind: feature
status: VERIFIED
title: "Handle rate limits"
sources: [S71]
---

# Handle rate limits

**Sources:** [S71](src.s71.md)

Fast mode has separate rate limits from standard Opus. All supported Opus models share one fast mode rate limit pool: usage on any of them draws from the same limits. When you hit the fast mode rate limit:
