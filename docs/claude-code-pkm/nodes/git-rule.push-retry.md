---
id: git-rule.push-retry
kind: git-rule
status: SESSION
title: "Retry network failures with backoff"
sources: [S8]
---

# Retry network failures with backoff

**Sources:** [S8](src.s8.md)

Retry network failures only, up to four times, with backoff of 2, 4, 8 and 16 seconds. Other failures are reported, not retried.
