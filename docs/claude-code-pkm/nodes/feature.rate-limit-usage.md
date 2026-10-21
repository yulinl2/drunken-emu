---
id: feature.rate-limit-usage
kind: feature
status: VERIFIED
title: "Rate limit usage"
sources: [S78]
---

# Rate limit usage

**Sources:** [S78](src.s78.md)

Display claude.ai subscription rate limit usage, or your spend against a Claude apps gateway spend limit, in the status line. For subscribers, the `rate_limits` object contains a rolling `five_hour` window and a weekly `seven_day` window. Each window provides `used_percentage`, from 0 to 100, and `resets_at`, the Unix epoch seconds when the window resets. Behind a gateway, read the `spend_limit` o
