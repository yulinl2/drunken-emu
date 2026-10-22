---
id: feature.api-request-body-event
kind: feature
status: VERIFIED
title: "API request body event"
sources: [S65]
---

# API request body event

**Sources:** [S65](src.s65.md)

Logged for each API request attempt when `OTEL_LOG_RAW_API_BODIES` is set. One event is emitted per attempt, so retries with adjusted parameters each produce their own event.
