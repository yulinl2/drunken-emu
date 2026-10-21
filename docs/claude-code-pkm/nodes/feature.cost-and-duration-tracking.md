---
id: feature.cost-and-duration-tracking
kind: feature
status: VERIFIED
title: "Cost and duration tracking"
sources: [S78]
---

# Cost and duration tracking

**Sources:** [S78](src.s78.md)

Track your session's API costs and elapsed time. The `cost.total_cost_usd` field accumulates the estimated cost of all API calls in the current session. The `cost.total_duration_ms` field measures the total time the session has been running, while `cost.total_api_duration_ms` tracks only the time spent waiting for API responses.
