---
id: feature.spend-limit-fields
kind: feature
status: VERIFIED
title: "Spend limit fields"
sources: [S78]
---

# Spend limit fields

**Sources:** [S78](src.s78.md)

Behind a Claude apps gateway with spend limits, the `rate_limits.spend_limit` object describes the spend limit that applies to you. It appears after the session's first API response and requires Claude Code v2.1.251 or later. Your script receives its fields on separate schedules:
